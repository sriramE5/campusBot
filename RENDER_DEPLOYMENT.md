# 🚀 CampusBot Render Deployment Guide

## 🎯 Why Render?
- **Free tier available** for both web services and databases
- **Easy GitHub integration**
- **Automatic deployments**
- **Built-in MongoDB** (or use external)
- **Custom domains supported**

## 📋 Step 1: Prepare Your Repository

### 1.1 Create GitHub Repository
```bash
git init
git add .
git commit -m "Ready for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/campusbot.git
git push -u origin main
```

### 1.2 Repository Structure
```
campusbot/
├── index.html              # Main login page
├── frontend/
│   └── index.html         # Chat interface
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.production
└── DEPLOYMENT.md
```

## 🔧 Step 2: Deploy Backend on Render

### 2.1 Create Render Web Service
1. **Sign up**: [Render](https://render.com)
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect GitHub**: Connect your repository
4. **Configure**:
   - **Name**: `campusbot-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.2 Environment Variables
Add these in Render dashboard:
```bash
GEMINI_API_KEY=your_gemini_api_key
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_production_secret
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=campusbot
NODE_ENV=production
```

### 2.3 Update CORS in Code
In `backend/main.py`, update line 59:
```python
allowed_origins = ["https://campusbot.onrender.com"]  # Your Render URL
```

## 🗄️ Step 3: Set Up Database

### Option A: Render PostgreSQL (Free)
1. **New PostgreSQL**: Click "New +" → "PostgreSQL"
2. **Configure**:
   - **Name**: `campusbot-db`
   - **Database Name**: `campusbot`
   - **User**: `campusbot`
3. **Get Connection String**: Copy internal connection URL

### Option B: MongoDB Atlas (Recommended)
1. Use existing MongoDB Atlas setup
2. Add Render's IP to MongoDB whitelist
3. Use Atlas connection string in environment variables

## 🎨 Step 4: Deploy Frontend on Render

### 4.1 Create Static Site Service
1. **New Static Site**: Click "New +" → "Static Site"
2. **Configure**:
   - **Name**: `campusbot-frontend`
   - **Root Directory**: `.` (project root)
   - **Build Command**: Leave empty (static files)
   - **Publish Directory**: `.`

### 4.2 Update Frontend URLs
In both HTML files, update:
```javascript
// index.html line 120
: 'https://campusbot-backend.onrender.com';

// frontend/index.html line 1518  
: 'https://campusbot-backend.onrender.com'; // Change to your deployed backend URL
```

## 🔗 Step 5: Configure Custom Domains (Optional)

### 5.1 Add Custom Domain
1. **Backend**: In web service settings → "Custom Domains"
2. **Frontend**: In static site settings → "Custom Domains"
3. **DNS**: Point your domain to Render's provided records

### 5.2 Update CORS Again
```python
allowed_origins = ["https://your-custom-domain.com"]
```

## ⚙️ Step 6: Render-Specific Configuration

### 6.1 Create render.yaml (Optional but Recommended)
Create `render.yaml` in project root:
```yaml
services:
  # Backend Service
  - type: web
    name: campusbot-backend
    env: python
    repo: https://github.com/yourusername/campusbot.git
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: MONGODB_URL
        sync: false
      - key: DATABASE_NAME
        sync: false
      - key: NODE_ENV
        value: production

  # Frontend Service
  - type: web
    name: campusbot-frontend
    env: static
    repo: https://github.com/yourusername/campusbot.git
    rootDir: .
    buildCommand: ""
    staticPublishPath: .
```

## 🚀 Step 7: Deploy!

### 7.1 Automatic Deployment
Once connected to GitHub, Render will:
- Auto-deploy on `git push`
- Rebuild when dependencies change
- Restart on failures

### 7.2 Manual Deployment
1. Push changes to GitHub
2. Render automatically detects and deploys
3. Monitor deployment logs in dashboard

## ✅ Step 8: Test Your Render App

### 8.1 Backend Test
Visit: `https://campusbot-backend.onrender.com/`
Should return: `{"message":"CampusBot Backend API"...}`

### 8.2 Frontend Test  
Visit: `https://campusbot.onrender.com`
Should show login page

### 8.3 Full Integration Test
1. Login with admin credentials
2. Test chat functionality
3. Add/remove events
4. Verify all features work

## 🛠️ Render-Specific Troubleshooting

### Common Issues:

**Port Issues**:
- Use `$PORT` environment variable in start command
- Render assigns ports dynamically

**Build Failures**:
- Check `requirements.txt` format
- Verify Python version compatibility
- Check build logs in Render dashboard

**Database Connection**:
- Use Render's internal connection strings
- Check firewall settings
- Verify environment variables

**CORS Problems**:
- Update allowed_origins with exact Render URL
- Include both HTTP and HTTPS if needed

**Static Site Issues**:
- Ensure files are in correct directory
- Check file permissions
- Verify build settings

## 📊 Render Free Tier Limits

### Backend (Web Service):
- **750 hours/month** (enough for 24/7)
- **512MB RAM**
- **Shared CPU**

### Frontend (Static Site):
- **Unlimited bandwidth**
- **Unlimited requests**
- **Custom SSL**

### Database:
- **PostgreSQL**: 256MB free
- **Or use external MongoDB Atlas**

## 🎉 Success Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible  
- [ ] Database connected successfully
- [ ] Login functionality works
- [ ] Chat functionality works
- [ ] Events management works
- [ ] CORS properly configured
- [ ] Custom domain configured (optional)
- [ ] SSL certificates active

## 💡 Pro Tips for Render

1. **Use render.yaml**: Infrastructure as code
2. **Monitor Logs**: Check Render dashboard regularly
3. **Set Up Alerts**: Get notified on failures
4. **Use Health Checks**: Render auto-restarts failed services
5. **Backup Database**: Regular exports from MongoDB Atlas

---

**🎊 Your CampusBot on Render will be live at:**
- **Backend**: `https://campusbot-backend.onrender.com`
- **Frontend**: `https://campusbot.onrender.com`

**Ready to deploy? Let me know if you need help with any step!**
