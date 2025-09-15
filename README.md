<<<<<<< HEAD
# CampusBot - University Campus Assistant 🤖
=======
# CampusBot - University Campus Assistant
<img width="1919" height="918" alt="image" src="https://github.com/user-attachments/assets/0431dfff-9931-40d4-85b2-8dfb323cd412" />
<img width="1916" height="904" alt="image" src="https://github.com/user-attachments/assets/bb1417ea-a3aa-489e-8348-5b96671af631" />



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

>>>>>>> a1ecae0d728aea56486f22db1885b2274898897d

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=flat&logo=github)](https://github.com/sriramE5/campusBot)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram)](https://telegram.org/)

A smart campus assistant bot that helps students and staff access university information, events, and services through an intuitive Telegram interface.
## 🌟 Features

### 🤖 Smart Assistant
- **Natural Language Processing**: Understands and responds to queries in natural language
- **24/7 Availability**: Always ready to assist with campus-related questions
- **Multi-topic Support**: Handles various queries from academics to campus facilities

### 📅 Event Management
- View upcoming campus events and activities
- Get event details including date, time, and location
- Filter events by category or date

### 🏛️ Campus Information
- Access to comprehensive knowledge base
- Find information about departments, facilities, and services
- Quick access to important documents and rules

### 🔍 Smart Search
- Semantic search across knowledge base
- Context-aware responses
- Continuously improving through interactions

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Telegram account
- Virtual environment (recommended)

### Installation

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

4. **Configure environment variables**
   Create a `.env` file in the `backend` directory with:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```
   Get your bot token from [@BotFather](https://t.me/botfather) on Telegram.

## 🏃‍♂️ Running the Bot

1. **Start the FastAPI server** (in the backend directory)
   ```bash
   uvicorn main:app --reload
   ```

2. **Run the Telegram bot** (in a new terminal)
   ```bash
   python telegram_bot.py
   ```

3. **Access the web interface** (optional)
   Open `frontend/index.html` in your web browser

## 🤖 Available Commands

- `/start` - Start interacting with the bot
- `/help` - Show help information
- `/events` - List upcoming campus events
- `[Any question]` - Ask about campus facilities, rules, or general information



## 🛠️ Technologies Used

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

## 📂 Project Structure

```
campusBot/
├── backend/
│   ├── data/                # Data files (events, etc.)
│   ├── knowledge_base/      # Text files with campus information
│   │   ├── college_data.txt
│   │   ├── hostelrules.txt
│   │   └── rules.txt
│   ├── faiss_index/         # Vector indices for semantic search
│   ├── __pycache__/
│   ├── main.py              # FastAPI application
│   ├── telegram_bot.py      # Telegram bot implementation
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html          # Main web interface
    └── locations.html      # Campus locations map
```

## 🔧 API Endpoints

The backend provides the following API endpoints:

- `GET /` - Health check endpoint
- `POST /api/chat` - Process chat messages
- `GET /api/events` - Get list of upcoming events
- `POST /api/events` - Add a new event (admin only)
- `GET /api/knowledge` - Search knowledge base

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the FastAPI and python-telegram-bot communities
- Icons by [Font Awesome](https://fontawesome.com/)

## 📚 Knowledge Base Management

The bot's knowledge is stored in text files within the `backend/knowledge_base/` directory. The main knowledge files are:

1. `college_data.txt` - General information about the university
2. `hostelrules.txt` - Rules and regulations for hostels
3. `rules.txt` - General campus rules and guidelines

### Updating the Knowledge Base

1. **Add or modify** the relevant text files in the `knowledge_base` directory
2. The system will automatically index the changes on the next restart
3. For immediate indexing, use the admin interface (if configured)

## 🔒 Security Considerations

- Always keep your `.env` file secure and never commit it to version control
- Use strong, unique passwords for admin access
- Regularly update dependencies to patch security vulnerabilities
- Monitor bot usage for any suspicious activity

## 🌐 Deployment

### Production Deployment

For production deployment, consider:

1. Using a production-grade ASGI server like Gunicorn with Uvicorn workers
2. Setting up proper logging and monitoring
3. Configuring HTTPS with a valid SSL certificate
4. Using environment variables for all sensitive configuration

### Example Gunicorn Command
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## 📈 Future Enhancements

- [ ] Add user authentication
- [ ] Implement more interactive features
- [ ] Expand knowledge base coverage
- [ ] Add support for multimedia responses
- [ ] Integrate with university calendar systems

## 🤝 Support

For support, please open an issue on the [GitHub repository](https://github.com/sriramE5/campusBot/issues).
