# CampusBot - Comprehensive Documentation

## 📝 Table of Contents
1. [Project Overview](#-project-overview)
2. [Features](#-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture](#-system-architecture)
5. [Installation Guide](#-installation-guide)
6. [Configuration](#-configuration)
7. [Usage Guide](#-usage-guide)
8. [API Documentation](#-api-documentation)
9. [Deployment](#-deployment)
10. [Troubleshooting](#-troubleshooting)
11. [Contributing](#-contributing)
12. [License](#-license)

## 🌟 Project Overview

CampusBot is an intelligent virtual assistant designed specifically for educational institutions. It provides students, faculty, and visitors with instant access to campus information, event details, and administrative services through an intuitive chat interface. The bot is accessible via Telegram and a web interface, making campus information available anytime, anywhere.

## ✨ Features

### 🤖 Smart Assistant
- Natural language processing for understanding queries
- 24/7 availability for campus-related information
- Context-aware responses
- Multi-language support (planned)

### 📅 Event Management
- View upcoming campus events
- Get event details (date, time, location, description)
- Filter events by category or date
- Event reminders and notifications

### 🏛️ Campus Information
- Department and faculty information
- Campus facilities and services
- Academic calendar and important dates
- Emergency contacts and procedures

### 🗺️ Campus Navigation
- Interactive campus maps
- Location-based services
- Building and facility locator

### 👨‍💼 Admin Features
- Content management system
- Event creation and management
- Analytics dashboard
- User management

## 💻 Technology Stack

### Backend
- **Python 3.13** - Core programming language
- **FastAPI** - Modern, fast web framework
- **python-telegram-bot** - Telegram bot framework
- **FAISS** - Efficient similarity search
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling
- **JavaScript** - Interactivity
- **Responsive Design** - Works on all devices

## 🏗️ System Architecture

```
campusBot/
├── backend/
│   ├── data/                # Data files (events, etc.)
│   ├── knowledge_base/      # Text files with campus information
│   ├── faiss_index/         # Vector indices for semantic search
│   ├── main.py              # FastAPI application
│   └── telegram_bot.py      # Telegram bot implementation
└── frontend/
    ├── index.html          # Main web interface
    └── locations.html      # Campus locations map
```

## 🛠️ Installation Guide

### Prerequisites
- Python 3.13 or higher
- pip (Python package manager)
- Telegram account (for bot interaction)
- Git (for version control)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/sriramE5/campusBot.git
   cd campusBot/backend
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. **Environment Variables**
   Create a `.env` file in the `backend` directory with:
   ```env
   # Required
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   
   # Optional
   API_BASE_URL=http://localhost:8000
   DEBUG=True
   ```

2. **Knowledge Base**
   Place your text files in the `backend/knowledge_base/` directory. The system will automatically index them on startup.

## 🚀 Usage Guide

### Starting the Application

1. **Start the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```

2. **Run the Telegram bot** (in a new terminal)
   ```bash
   python telegram_bot.py
   ```

3. **Access the web interface**
   Open `frontend/index.html` in a web browser

### Basic Commands
- `/start` - Start interacting with the bot
- `/help` - Show help information
- `/events` - List upcoming campus events

## 📚 API Documentation

### Endpoints

#### Chat
- `POST /api/chat` - Process chat messages
  ```json
  {
    "message": "Your message here",
    "user_id": "unique_user_id"
  }
  ```

#### Events
- `GET /api/events` - Get list of upcoming events
- `POST /api/events` - Add a new event (admin only)
- `GET /api/events/{event_id}` - Get event details

## 🚀 Deployment

### Production Deployment

1. **Set up a production server**
   - Use Gunicorn with Uvicorn workers
   - Configure Nginx as a reverse proxy
   - Set up SSL/TLS with Let's Encrypt

2. **Environment Configuration**
   - Set `DEBUG=False` in production
   - Configure proper logging
   - Set up monitoring and alerts

### Example Gunicorn Command
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot is running
   - Verify the Telegram bot token
   - Check server logs for errors

2. **Knowledge base not updating**
   - Ensure files are in the correct directory
   - Check file permissions
   - Restart the application

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the FastAPI and python-telegram-bot communities
- Icons by [Font Awesome](https://fontawesome.com/)

---

📅 *Last Updated: September 2025*
