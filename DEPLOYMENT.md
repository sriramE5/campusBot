# 🚀 CampusBot Deployment Guide

## 📋 Prerequisites
- Node.js 16+ (for some deployment platforms)
- MongoDB Atlas account (free tier available)
- Domain name (optional)
- Git repository

## 🗄️ Step 1: Set Up MongoDB Atlas

1. **Create Account**: Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create Cluster**: 
   - Choose "Shared Cluster" (free tier)
   - Select a cloud provider and region
3. **Create Database User**:
   - Username: `campusbot`
   - Password: Generate a strong password
4. **Whitelist IP**: 
   - For development: Add your current IP
   - For production: Add `0.0.0.0/0` (allows all access)
5. **Get Connection String**:
   - Click "Connect" → "Connect your application"
   - Copy the connection string

## 🔧 Step 2: Configure Environment Variables

### Backend Configuration
Create `.env.production` in backend folder:

```bash
GEMINI_API_KEY=your_gemini_api_key
ADMIN_PASSWORD=your_secure_admin_password
SECRET_KEY=your_production_secret_key
MONGODB_URL=mongodb+srv://campusbot:YOUR_PASSWORD@cluster.mongodb.net/campusbot
DATABASE_NAME=campusbot
NODE_ENV=production
```

### Frontend Configuration
Update the API_BASE_URL in both HTML files:

**index.html** (line 120):
```javascript
: 'https://your-backend-domain.com';
```

**frontend/index.html** (line 1518):
```javascript
: 'https://your-backend-domain.com'; // Change to your deployed backend URL
```

**Backend CORS** (main.py line 59):
```python
allowed_origins = ["https://your-frontend-domain.com"]
```

## 🌐 Step 3: Deploy Backend

### Option A: Railway (Recommended)
1. **Install Railway CLI**: `npm install -g @railway/cli`
2. **Login**: `railway login`
3. **Initialize**: `railway init` in backend folder
4. **Deploy**: `railway up`
5. **Set Environment Variables** in Railway dashboard
6. **Get URL**: Railway will provide a `.railway.app` domain

### Option B: Vercel
1. **Install Vercel CLI**: `npm i -g vercel`
2. **Configure vercel.json**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```
3. **Deploy**: `vercel --prod` in backend folder

### Option C: DigitalOcean
1. Create Droplet with Ubuntu
2. Install dependencies: `pip install -r requirements.txt`
3. Use PM2 for process management
4. Configure Nginx as reverse proxy

## 🎨 Step 4: Deploy Frontend

### Option A: Vercel (Easiest)
1. **Push to GitHub**: Upload your code to GitHub
2. **Connect Vercel**: Connect your GitHub repository
3. **Configure**: 
   - Root directory: `./`
   - Build command: None (static files)
   - Output directory: `./`
4. **Deploy**: Automatic deployment

### Option B: Netlify
1. **Drag & Drop**: Drag the project folder to Netlify
2. **Configure**: Set up custom domain if needed
3. **Deploy**: Automatic deployment

## 🔐 Step 5: Update Configuration

After deployment, update these values:

### In Frontend Files:
- Replace `your-backend-domain.com` with your actual backend URL
- Example: `https://campusbot-backend.railway.app`

### In Backend Code:
- Replace `your-frontend-domain.com` with your actual frontend URL
- Example: `https://campusbot.vercel.app`

## ✅ Step 6: Test Deployment

1. **Backend Health**: Visit `https://your-backend-domain.com/`
2. **Frontend Access**: Visit `https://your-frontend-domain.com`
3. **Login Test**: Try admin login
4. **Chat Test**: Test the chat functionality
5. **Events Test**: Add/remove events

## 🛠️ Troubleshooting

### Common Issues:

**CORS Errors**:
- Check allowed_origins in backend
- Verify frontend URL matches exactly

**Database Connection**:
- Verify MongoDB connection string
- Check IP whitelist in MongoDB Atlas
- Ensure user credentials are correct

**API Key Issues**:
- Verify GEMINI_API_KEY is valid
- Check environment variables are set correctly

**Deployment Failures**:
- Check logs in deployment platform
- Verify all dependencies are installed
- Ensure Python version compatibility

## 📱 Production Checklist

- [ ] MongoDB Atlas configured
- [ ] Environment variables set
- [ ] CORS properly configured
- [ ] HTTPS enabled
- [ ] Custom domain configured
- [ ] API keys secured
- [ ] Error monitoring set up
- [ ] Backup strategy implemented

## 🔗 Useful Links

- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [Railway](https://railway.app)
- [Vercel](https://vercel.com)
- [Netlify](https://netlify.com)
- [Google AI Studio](https://aistudio.google.com/app/apikey)

## 💡 Pro Tips

1. **Use Custom Domains**: More professional than default domains
2. **Monitor Performance**: Use tools like Uptime Robot
3. **Set Up Analytics**: Google Analytics for user insights
4. **Regular Backups**: Export MongoDB data regularly
5. **Security**: Regularly update dependencies and change passwords

---

**🎉 Your CampusBot is now ready for production deployment!**
