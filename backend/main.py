import os
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import time
import threading

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from bson import ObjectId

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
BASE_DIR = Path(__file__).resolve().parent

# Load environment based on NODE_ENV
ENV = os.getenv("NODE_ENV", "development")
if ENV == "production":
    load_dotenv(BASE_DIR / ".env.production")
else:
    load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
SECRET_KEY = os.getenv("SECRET_KEY", "devsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campusbot")

# Initialize MongoDB client with better error handling
try:
    import urllib.parse
    
    # Parse the MongoDB URL and encode username/password if needed
    if "@" in MONGODB_URL:
        # Extract the part before @ and encode it
        auth_part, rest = MONGODB_URL.split("@", 1)
        if "://" in auth_part:
            protocol, credentials = auth_part.split("://", 1)
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                # URL encode username and password
                encoded_username = urllib.parse.quote_plus(username)
                encoded_password = urllib.parse.quote_plus(password)
                MONGODB_URL = f"{protocol}://{encoded_username}:{encoded_password}@{rest}"
    
    client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=30000,  # 30 seconds
        connectTimeoutMS=30000,           # 30 seconds  
        socketTimeoutMS=30000,            # 30 seconds
        retryWrites=True,
        w="majority"
    )
    db = client[DATABASE_NAME]
    print(f"MongoDB client initialized successfully for database: {DATABASE_NAME}")
except Exception as e:
    print(f"Failed to initialize MongoDB client: {e}")
    client = None
    db = None

if GEMINI_API_KEY:
    os.environ.setdefault("GEMINI_API_KEY", GEMINI_API_KEY)
    os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)

app = FastAPI(title="Full-Stack Campus Helper - Backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins
        "https://auscampusbot.loopminds.in",  # Your deployed frontend domain
        "https://campusbot-biat.onrender.com",  # Your backend domain
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Local development
        "http://localhost:8000",  # Local backend
        "http://127.0.0.1:8000",  # Local backend
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Paths
DATA_DIR = BASE_DIR / "data"
KB_DIR = BASE_DIR / "knowledge_base"
FAISS_DIR = BASE_DIR / "faiss_index"
DATA_DIR.mkdir(exist_ok=True)
KB_DIR.mkdir(exist_ok=True)
FAISS_DIR.mkdir(exist_ok=True)

EVENTS_FILE = DATA_DIR / "events.json"

# RAG configuration
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"

app.state.vectorstore: Optional[FAISS] = None
app.state.embeddings = None

class ChatRequest(BaseModel):
    message: str

class EventIn(BaseModel):
    name: str
    date: str  
    location: str
    details: str

class Event(EventIn):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

# MongoDB Models
class EventDocument(BaseModel):
    _id: Optional[ObjectId] = None
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    date: str
    location: str
    details: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserDocument(BaseModel):
    _id: Optional[ObjectId] = None
    username: str
    password_hash: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

# MongoDB Helper Functions
async def get_events_from_db() -> List[Event]:
    """Get all events from MongoDB"""
    if not db:
        print("Database not available - returning empty events list")
        return []
    
    try:
        events_cursor = db.events.find({}).sort("created_at", -1)
        events = []
        async for event_doc in events_cursor:
            event_doc["id"] = str(event_doc.pop("_id"))
            events.append(Event(**event_doc))
        return events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

async def add_event_to_db(event_data: EventIn) -> Event:
    """Add a new event to MongoDB"""
    if not db:
        print("Database not available - cannot add event")
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        event_doc = EventDocument(**event_data.dict())
        result = await db.events.insert_one(event_doc.dict())
        event_doc.id = str(result.inserted_id)
        return Event(**event_doc.dict())
    except Exception as e:
        print(f"Error adding event: {e}")
        raise HTTPException(status_code=500, detail="Failed to add event")

async def delete_event_from_db(event_id: str) -> bool:
    """Delete an event from MongoDB"""
    if not db:
        print("Database not available - cannot delete event")
        return False
    
    try:
        result = await db.events.delete_one({"id": event_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False

async def get_user_by_username(username: str) -> Optional[UserDocument]:
    """Get user by username from MongoDB"""
    if not db:
        print("Database not available - cannot get user")
        return None
    
    try:
        user_doc = await db.users.find_one({"username": username})
        if user_doc:
            user_doc["id"] = str(user_doc.pop("_id"))
            return UserDocument(**user_doc)
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

async def create_default_admin():
    """Create default admin user if not exists"""
    if not db:
        print("Database not available - cannot create admin user")
        return
    
    try:
        existing_admin = await db.users.find_one({"username": "admin"})
        if not existing_admin:
            import hashlib
            password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
            admin_user = UserDocument(
                username="admin",
                password_hash=password_hash,
                is_admin=True
            )
            await db.users.insert_one(admin_user.dict())
            print("Created default admin user")
    except Exception as e:
        print(f"Error creating admin user: {e}")

# Database initialization
async def init_db():
    """Initialize database with default data"""
    if not client:
        print("MongoDB client not available - skipping database initialization")
        return
    
    try:
        # Test connection first
        await client.admin.command('ping')
        print("MongoDB connection successful")
        
        await create_default_admin()
        
        # Create indexes for better performance
        await db.events.create_index("id", unique=True)
        await db.events.create_index("date")
        await db.users.create_index("username", unique=True)
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Continue without database - app will work but some features won't
        return



# Authentication (JWT)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def admin_required(authorization: Optional[str] = Header(None)):
    """Dependency to protect admin endpoints."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def build_faiss_index():
    """Build FAISS vector store from knowledge_base files."""
    print("Building FAISS index from knowledge_base...") 

    loaders = {
        ".pdf": PyPDFLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader,
        ".txt": DirectoryLoader,
        ".html": UnstructuredHTMLLoader,
        ".json": JSONLoader,
    }

    all_docs = []
    
    for file_extension, loader_class in loaders.items():
        if file_extension in [".txt", ".json"]:  # DirectoryLoader and JSONLoader need special handling
            if file_extension == ".txt":
                loader = DirectoryLoader(str(KB_DIR), glob=f"**/*{file_extension}")
                raw_docs = loader.load()
            else: 
                for file_path in KB_DIR.glob(f'**/*{file_extension}'):
                    try:
                        loader = JSONLoader(file_path=str(file_path), jq_schema='.', text_content=False)
                        raw_docs = loader.load()
                        all_docs.extend(raw_docs)
                    except Exception as e:
                        print(f"Failed to load JSON file {file_path}: {e}")
                continue
        else:
            loader = DirectoryLoader(str(KB_DIR), glob=f"**/*{file_extension}", loader_cls=loader_class)
            raw_docs = loader.load()
        
        all_docs.extend(raw_docs)

    if not all_docs:
        print("No documents found in knowledge_base.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents(all_docs)

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(str(FAISS_DIR))

    app.state.embeddings = embeddings
    app.state.vectorstore = vectorstore
    print("FAISS index built and saved to:", FAISS_DIR)

def load_faiss_index_if_exists():
    if not FAISS_DIR.exists() or not any(FAISS_DIR.iterdir()):
        return None
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    try:
        vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
        app.state.vectorstore = vectorstore
        app.state.embeddings = embeddings
        print("Loaded FAISS vectorstore from disk.")
        return vectorstore
    except Exception as e:
        print("Failed to load FAISS index:", e)
        return None



class KnowledgeBaseEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}. Re-indexing...")
            build_faiss_index()

def start_file_watcher():
    event_handler = KnowledgeBaseEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(KB_DIR), recursive=True)
    observer.start()
    print("Started file watcher for knowledge base directory.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB
    await init_db()
    print("MongoDB initialized successfully")

    if not load_faiss_index_if_exists():
        try:
            build_faiss_index()
        except Exception as exc:
            print("Error during FAISS index build:", exc)

    watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
    watcher_thread.start()



@app.get("/")
async def root():
    return {"message": "CampusBot Backend API", "docs": "/docs", "version": "1.0.0"}

# Chat endpoint(RAG)

@app.options("/chat")
async def chat_options():
    
    return JSONResponse(content={"message": "ok"})


@app.post("/chat")
async def chat_endpoint(chat_req: ChatRequest):
    user_question = chat_req.message.strip()
    if not user_question:
        raise HTTPException(status_code=400, detail="Empty message")

    # Try to load FAISS index if not available
    if not app.state.vectorstore:
        if not load_faiss_index_if_exists():
            try:
                build_faiss_index()
            except Exception as e:
                print(f"FAISS index build failed: {e}")
    
    # If vector store is still not available, provide fallback response
    if not app.state.vectorstore:
        return {
            "response": f"I apologize, but I'm currently experiencing technical difficulties with my knowledge base. However, I can still help you with general questions about Aditya University. You asked: '{user_question}'. For specific campus information, please try again later or contact the administration office."
        }

    try:
        top_docs: List[Document] = app.state.vectorstore.similarity_search(user_question, k=3)
    except Exception as e:
        print(f"Vector search error: {e}")
        return {
            "response": f"I apologize, but I'm experiencing issues with my search functionality. You asked: '{user_question}'. Please try again later or contact the administration for assistance."
        }

    docs_texts = [d.page_content for d in top_docs]
    events = await get_events_from_db()
    events_json = json.dumps([e.dict() for e in events], indent=2, ensure_ascii=False)

    system_message = (
        "You are Campus AI assistant of Aditya University. Answer relevant content from provided context.\n"
        "structured JSON data is provided for upcoming events. Use it to answer event-related queries.\n"
        "If the answer is not in the context, respond with 'I don't know'. Be concise."
        "Use formal language suitable for students and faculty."
        "semantic search the documents for relevant info."
        "respond for every user query even it is not related to context. Do not say I don't know. Be creative."
    )

    docs_block = "\n\n--- DOCUMENTS ---\n"
    for i, txt in enumerate(docs_texts, 1):
        docs_block += f"\n[Document {i}]\n{txt}\n"

    events_block = "\n\n--- EVENTS (structured JSON) ---\n```json\n" + events_json + "\n```\n"

    human_message = (
        f"{docs_block}{events_block}\n\n"
        f"User question: {user_question}\n\n"
        "Answer using only the context above."
    )

    try:
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.0)
        response = llm.invoke([("system", system_message), ("human", human_message)])
        text = getattr(response, "content", str(response))
    except Exception as e:
        print(f"LLM error: {e}")
        return {
            "response": f"I apologize, but I'm experiencing issues with my AI response generation. You asked: '{user_question}'. Please try again later or contact the administration for assistance."
        }

    return {"response": text}

@app.get("/events")
async def get_events():
    """Get all events from MongoDB"""
    events = await get_events_from_db()
    return [e.dict() for e in events]


@app.post("/events")
async def add_event(event_in: EventIn, auth=Depends(admin_required)):
    """Add a new event to MongoDB"""
    try:
        new_event = await add_event_to_db(event_in)
        return new_event.dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Add event error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add event due to database issues")

@app.delete("/events/{event_id}")
async def delete_event(event_id: str, auth=Depends(admin_required)):
    """Delete an event from MongoDB"""
    success = await delete_event_from_db(event_id)
    if success:
        return {"message": "Event deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Event not found")

@app.post("/signup")
async def signup(signup_request: SignupRequest):
    """Register a new user"""
    import hashlib
    
    # Check if database is available
    if not db:
        raise HTTPException(status_code=503, detail="Database not available for signup")
    
    # Check if user already exists
    existing_user = await get_user_by_username(signup_request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    password_hash = hashlib.sha256(signup_request.password.encode()).hexdigest()
    new_user = UserDocument(
        username=signup_request.username,
        password_hash=password_hash,
        is_admin=False
    )
    
    try:
        await db.users.insert_one(new_user.dict())
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.options("/login")
async def login_options():
    return JSONResponse(content={"message": "ok"})

@app.post("/login")
async def login(login_request: LoginRequest):
    """Authenticate user with MongoDB or fallback"""
    import hashlib
    
    print(f"Login attempt for user: {login_request.username}")
    
    # Fallback to hardcoded admin credentials for when MongoDB is not available OR for admin user
    if login_request.username == "admin" and login_request.password == ADMIN_PASSWORD:
        print("Using fallback authentication - SUCCESS")
        access_token = create_access_token(data={"sub": "admin"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    
    print("Admin credentials not matched, trying MongoDB...")
    
    # Try MongoDB authentication for non-admin users
    if db:
        user = await get_user_by_username(login_request.username)
        
        if user:
            # Verify password
            password_hash = hashlib.sha256(login_request.password.encode()).hexdigest()
            if user.password_hash == password_hash:
                print("MongoDB authentication - SUCCESS")
                # Update last login
                try:
                    await db.users.update_one(
                        {"username": login_request.username},
                        {"$set": {"last_login": datetime.utcnow()}}
                    )
                except:
                    pass  # Continue even if update fails
                
                access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
                return {"access_token": access_token, "token_type": "bearer"}
    
    print("Authentication failed - INVALID CREDENTIALS")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@app.post("/admin/reindex")
async def reindex(background_tasks: BackgroundTasks, auth=Depends(admin_required)):
    background_tasks.add_task(build_faiss_index)
    return {"message": "Reindexing started in background."}

