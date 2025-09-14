# CampusBot - University Campus Assistant
<img width="1919" height="918" alt="image" src="https://github.com/user-attachments/assets/0431dfff-9931-40d4-85b2-8dfb323cd412" />
<img width="1919" height="918" alt="image" src="https://github.com/user-attachments/assets/06a01a73-8a5c-4e3e-ad4a-26a23c5a2c28" />


githublink : https://github.com/sriramE5/campusBot
## 📱 Application Overview

CampusBot is an intelligent virtual assistant designed specifically for Aditya University, providing a seamless interface for students, faculty, and visitors to access campus information, events, and services. The application combines AI-powered chat functionality with comprehensive campus resources to enhance the university experience.

### Key Components:
- **Interactive Chat Interface**: Natural language processing for intuitive Q&A
- **Campus Navigation**: Interactive maps and location services
- **Event Management System**: Comprehensive calendar and event tracking
- **Administrative Dashboard**: Secure interface for content management
- **Knowledge Repository**: Centralized access to university information

## 🗺️ Campus Maps & Navigation

The application features an interactive campus map system that helps users:
- Locate buildings, departments, and facilities
- Access detailed information about each location
- View location-specific resources

The map interface is integrated with the chat system, allowing users to ask questions like "Where is the library?" and receive both a text response and a visual map location.

## 👨‍💼 Admin Features

The admin panel provides authorized personnel with powerful tools to manage the application:

### User Management
- Create and manage admin accounts
- Set access levels and permissions
- Monitor user activity and interactions

### Content Management
- Update knowledge base documents
- Manage FAQ database
- Moderate user-generated content
- Track content updates and revisions

### System Configuration
- Configure application settings
- Manage integrations with other university systems
- Set up automated notifications and alerts

### Analytics Dashboard
- View usage statistics
- Track popular queries and searches
- Generate reports on system performance

## 🗓️ Events System

The comprehensive event management system allows for:

### Event Creation & Management
- Add, edit, and remove events
- Set event details (date, time, location, description)
- Categorize events (academic, social, sports, etc.)
- Upload event images and attachments

### Event Discovery
- Browse upcoming events
- Filter by category, date, or location
- Save events to personal calendar
- Set event reminders



## 🌟 Features

- **AI-Powered Chat Interface**: Natural language processing for understanding and responding to user queries
- **Event Management**: View, add, and manage university events (admin-only)
- **Knowledge Base**: Access to university information, rules, and regulations
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Voice Input**: Speech-to-text functionality for hands-free interaction
- **Admin Dashboard**: Secure interface for managing content and events

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for frontend development)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/campusBot.git
   cd campusBot
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `backend` directory with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   ADMIN_PASSWORD=your_secure_password
   SECRET_KEY=your_secret_key
   ```

4. **Initialize the knowledge base**
   ```bash
   python main.py
   ```
   The first run will build the FAISS index from the knowledge base files.

5. **Set up the frontend**
   ```bash
   cd ../frontend
   # No build step required as it's plain HTML/JS
   ```

6. **Run the application**
   - Start the backend server (from the `backend` directory):
     ```bash
     uvicorn main:app --reload
     ```
   - Open `frontend/index.html` in a web browser

## 🛠️ Project Structure

```
campusBot/
├── backend/
│   ├── data/               # Data storage
│   ├── faiss_index/        # Vector store for semantic search
│   ├── knowledge_base/     # Source documents for the knowledge base
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html         # Main application interface
│   └── locations.html     # Campus locations page
└── README.md              # This file
```

## 🔧 API Endpoints

- `POST /api/chat` - Send a message to the chatbot
- `GET /api/events` - Get list of upcoming events
- `POST /api/events` - Add a new event (admin)
- `DELETE /api/events/{event_id}` - Delete an event (admin)
- `POST /api/admin/login` - Admin authentication
- `POST /api/admin/reindex` - Rebuild search index (admin)

## 🤖 How It Works

The CampusBot uses a combination of:
- **Google's Gemini AI** for natural language understanding
- **FAISS** for efficient similarity search in the knowledge base
- **FastAPI** for the backend server
- **Vanilla JavaScript** for the frontend interface

## 📚 Knowledge Base

The bot's knowledge comes from text files in the `backend/knowledge_base/` directory. To update the knowledge base:
1. Add or modify files in the `knowledge_base` directory
2. The system will automatically detect changes and update the index
3. Or manually trigger a reindex from the admin interface

## 🔒 Admin Access

Admin features include:
- Adding/removing events
- Rebuilding the knowledge base index
- Managing university information

To access admin features:
1. Click the admin icon in the sidebar
2. Enter the admin password (set in `.env`)
3. Use the admin controls that appear

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- FastAPI for the backend framework
- FAISS for efficient similarity search
- All contributors who helped build this project
