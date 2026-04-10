# Render Deployment Guide

## Prerequisites
- GitHub repository created and code pushed
- Render account (free tier available at https://render.com)

## Deployment Steps

### Step 1: Prepare Your Repository
All necessary files are already set up:
- ✅ `Procfile` - Specifies how to run the app
- ✅ `render.yaml` - Optional configuration file
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `.gitignore` - Excludes unnecessary files

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign in or create an account

2. **Create a New Web Service**
   - Click "New +" button
   - Select "Web Service"

3. **Connect GitHub Repository**
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your repository: `Intelligent-Queue-Prediction-and-Management-System-for-Smart-Campuses`

4. **Configure Service**
   - **Name**: `intelligent-queue-system` (or your preferred name)
   - **Branch**: `master`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid if you prefer)
   - **Region**: Choose closest to you

5. **Add Environment Variables** (Optional)
   - Click "Environmental Variables"
   - Add any sensitive variables needed:
     - `FLASK_ENV`: `production`
     - `SECRET_KEY`: Generate a secure key (use Python: `python -c "import secrets; print(secrets.token_hex(32))"`)

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Watch the logs for any issues

### Step 3: Update Your Flask App (Optional but Recommended)

For production, consider updating your app.py to use environment variables:

```python
import os
from flask import Flask

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.getenv('FLASK_ENV') != 'production'
```

### Step 4: Monitor Your Deployment

- Render provides free SSL certificate (HTTPS)
- Check the Logs tab for any errors
- Your app will be available at: `https://your-service-name.onrender.com`

### Notes

- Free tier on Render may spin down after 15 minutes of inactivity
- Database (SQLite) will be ephemeral on free tier
- For production, consider using PostgreSQL instead of SQLite

## Troubleshooting

If deployment fails:
1. Check the Logs tab in Render dashboard
2. Ensure all dependencies in `requirements.txt` are correct
3. Verify `Procfile` has no trailing spaces
4. Make sure app runs locally first: `python app.py`

## Update and Redeploy

After making changes:
```bash
git add .
git commit -m "Your message"
git push origin master
```

Render will automatically detect changes and redeploy!
