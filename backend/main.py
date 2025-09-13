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
from pydantic import BaseModel
from jose import jwt, JWTError

# LangChain & Google Gemini integration
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredHTMLLoader, JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# File system watcher
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Load environment
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Required environment variables (placeholders in .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
SECRET_KEY = os.getenv("SECRET_KEY", "devsecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Ensure Gemini env var reachable by libs that check GOOGLE_API_KEY or GEMINI_API_KEY
if GEMINI_API_KEY:
    os.environ.setdefault("GEMINI_API_KEY", GEMINI_API_KEY)
    os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)

app = FastAPI(title="Full-Stack Campus Helper - Backend")

# Allow the frontend dev server(s). Adjust as needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DATA_DIR = BASE_DIR / "data"
KB_DIR = BASE_DIR / "knowledge_base"
FAISS_DIR = BASE_DIR / "faiss_index"
DATA_DIR.mkdir(exist_ok=True)
KB_DIR.mkdir(exist_ok=True)
FAISS_DIR.mkdir(exist_ok=True)

EVENTS_FILE = DATA_DIR / "events.json"

# RAG / Embedding model configuration
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"

# Application state
app.state.vectorstore: Optional[FAISS] = None
app.state.embeddings = None


# ------------------------
# Pydantic models
# ------------------------
class ChatRequest(BaseModel):
    message: str


class EventIn(BaseModel):
    name: str
    date: str  # ISO format YYYY-MM-DD
    location: str
    details: str


class Event(EventIn):
    id: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ------------------------
# Utility: events file read/write
# ------------------------
def read_events() -> List[Event]:
    if not EVENTS_FILE.exists():
        EVENTS_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Event(**e) for e in data]
    except Exception:
        return []


def write_events(events: List[Event]):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump([e.dict() for e in events], f, indent=2, ensure_ascii=False)


# ------------------------
# Authentication (JWT)
# ------------------------
# Check for this type of issue right before your function starts
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
# There should be no misplaced characters here, and the indentation for the next function should be correct.
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


# ------------------------
# RAG Index functions
# ------------------------
def build_faiss_index():
    """Build FAISS vector store from knowledge_base files."""
    print("Building FAISS index from knowledge_base...")
    
    # Use different loaders for different file types
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
            else: # .json
                # This glob pattern needs a dedicated loader instance
                for file_path in KB_DIR.glob(f'**/*{file_extension}'):
                    try:
                        loader = JSONLoader(file_path=str(file_path), jq_schema='.', text_content=False)
                        raw_docs = loader.load()
                        all_docs.extend(raw_docs)
                    except Exception as e:
                        print(f"Failed to load JSON file {file_path}: {e}")
                continue # Skip the general loader
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


# ------------------------
# File Watcher
# ------------------------
class KnowledgeBaseEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}. Re-indexing...")
            # Use a background task or a separate thread to avoid blocking the main server loop
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


# ------------------------
# Startup
# ------------------------
@app.on_event("startup")
def startup_event():
    # Seed events.json if empty
    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size == 0:
        sample_events = [
            {
                "id": str(uuid.uuid4()),
                "name": "Orientation Day",
                "date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "location": "Main Auditorium",
                "details": "Welcome and orientation for new students."
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Coding Club Meetup",
                "date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "location": "Lab 204",
                "details": "Discussing algorithms and interview prep."
            }
        ]
        write_events([Event(**e) for e in sample_events])
        print("Initialized events.json with sample data.")

    if not load_faiss_index_if_exists():
        try:
            build_faiss_index()
        except Exception as exc:
            print("Error during FAISS index build:", exc)
    
    # Start the file watcher in a new thread
    watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
    watcher_thread.start()


# ------------------------
# Chat endpoint (RAG)
# ------------------------
@app.options("/chat")
async def chat_options():
    """Handle preflight requests for /chat"""
    return JSONResponse(content={"message": "ok"})


@app.post("/chat")
async def chat_endpoint(chat_req: ChatRequest):
    user_question = chat_req.message.strip()
    if not user_question:
        raise HTTPException(status_code=400, detail="Empty message")

    if not app.state.vectorstore:
        if not load_faiss_index_if_exists():
            build_faiss_index()
    if not app.state.vectorstore:
        raise HTTPException(status_code=500, detail="Vector store not available.")

    try:
        top_docs: List[Document] = app.state.vectorstore.similarity_search(user_question, k=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during retrieval: {e}")

    docs_texts = [d.page_content for d in top_docs]
    events = read_events()
    events_json = json.dumps([e.dict() for e in events], indent=2, ensure_ascii=False)

    system_message = (
        "You are Campus Helper Chatbot of Aditya University. Answer relevant content from provided context.\n"
        "structured JSON data is provided for upcoming events. Use it to answer event-related queries.\n"
        "If the answer is not in the context, respond with 'I don't know'. Be concise."
        "Use formal language suitable for students and faculty."
        "semantic search the documents for relevant info."
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

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.0)
    try:
        response = llm.invoke([("system", system_message), ("human", human_message)])
        text = getattr(response, "content", str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation error: {e}")

    return {"response": text}


# ------------------------
# Events endpoints
# ------------------------
@app.get("/events")
async def get_events():
    return [e.dict() for e in read_events()]


@app.post("/events")
async def add_event(event_in: EventIn, auth=Depends(admin_required)):
    events = read_events()
    new_event = Event(id=str(uuid.uuid4()), **event_in.dict())
    events.append(new_event)
    write_events(events)
    return new_event.dict()


@app.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: str, auth=Depends(admin_required)):
    events = read_events()
    filtered = [e for e in events if e.id != event_id]
    if len(filtered) == len(events):
        raise HTTPException(status_code=404, detail="Event not found")
    write_events(filtered)
    return None


# ------------------------
# Admin: login (get JWT)
# ------------------------
@app.post("/login")
async def login(req: LoginRequest):
    if req.username != "admin" or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": "admin"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------
# Admin: reindex endpoint
# ------------------------
@app.post("/admin/reindex")
async def reindex(background_tasks: BackgroundTasks, auth=Depends(admin_required)):
    background_tasks.add_task(build_faiss_index)
    return {"message": "Reindexing started in background."}

