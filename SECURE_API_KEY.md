# 🔒 Secure API Key Setup with GitHub Secrets

## 🚨 Security Issue Fixed:
Your API key was exposed in the repository. Now it uses GitHub environment variables.

## 📋 Steps to Add GitHub Secrets:

### 1. Go to Your GitHub Repository
- Navigate to your repository: `https://github.com/sriramE5/campusBot`
- Go to **Settings** tab

### 2. Add Repository Secrets
- Click **Secrets and variables** → **Actions**
- Click **New repository secret**
- Add these secrets:

#### Secret 1: GEMINI_API_KEY
- **Name**: `GEMINI_API_KEY`
- **Value**: `AIzaSyAj7i6Pvo69c8Q1-K6ihX14-kqQoUXQr9E`
- Click **Add secret**

#### Secret 2: MONGODB_URL (Optional)
- **Name**: `MONGODB_URL`
- **Value**: `mongodb+srv://campusbot:campusbot123@campusbot.w3qwnk6.mongodb.net/campusbot?retryWrites=true&w=majority`
- Click **Add secret**

### 3. Update Render Environment
Go to your Render dashboard:
- Select your backend service
- Go to **Environment** tab
- Add environment variable:
  - **Key**: `GEMINI_API_KEY`
  - **Value**: `AIzaSyAj7i6Pvo69c8Q1-K6ihX14-kqQoUXQr9E`

## ✅ Benefits:
- 🔒 API key not exposed in code
- 🔒 Secure storage in GitHub
- 🔒 Render can access via environment variables
- 🔒 No more security risk

## 🚀 Deploy Changes:
```bash
git add .
git commit -m "Secure API key with GitHub environment variables"
git push
```

## 📊 Current Status:
- ✅ API key removed from repository
- ✅ Using GitHub environment variables
- ✅ Ready for secure deployment
- ✅ No more security exposure
