# Deployment Guide - SHL Assessment Recommendation System

## Where to Deploy?

The assignment suggests using **free cloud platforms**. Here are the best options:

---

## ✅ RECOMMENDED: Render.com (FREE & EASIEST)

### Why Render?
- ✅ FREE tier available
- ✅ No credit card required
- ✅ Automatic HTTPS
- ✅ Simple deployment from GitHub
- ✅ Environment variables support

### Deployment Steps:

#### 1. Prepare Your Repository
```bash
# Make sure all files are committed
cd ""
git init
git add .
git commit -m "Initial commit - SHL Assessment Recommendation System"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/shl-assessment-recommender.git
git push -u origin main
```

#### 2. Deploy on Render

1. Go to: https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `shl-assessment-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free`

6. Add Environment Variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: Your Gemini API key

7. Click "Create Web Service"

#### 3. Your API will be live at:
```
https://shl-assessment-api.onrender.com
```

**Test it**:
```bash
curl https://shl-assessment-api.onrender.com/health
```

---

## Option 2: Railway.app (FREE)

### Why Railway?
- ✅ $5 free credit per month
- ✅ Very fast deployment
- ✅ Auto-scaling

### Deployment:
1. Go to: https://railway.app
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variable: `GEMINI_API_KEY`
6. Railway auto-detects Python and deploys

---

## Option 3: Google Cloud Run (FREE Tier)

### Why Cloud Run?
- ✅ 2 million requests/month free
- ✅ Google infrastructure
- ✅ Auto-scaling

### Quick Deploy:
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Deploy
gcloud run deploy shl-assessment-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key_here
```

---

## Option 4: Heroku (Requires Credit Card)

### Setup:
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create shl-assessment-api

# Set environment variable
heroku config:set GEMINI_API_KEY=your_key_here

# Deploy
git push heroku main

# Open
heroku open
```

---

## Option 5: PythonAnywhere (FREE)

### Why PythonAnywhere?
- ✅ Always-free tier
- ✅ Python-specific hosting
- ✅ Simple setup

### Steps:
1. Sign up at: https://www.pythonanywhere.com
2. Upload your files
3. Set up web app in dashboard
4. Configure WSGI file
5. Add environment variables in web tab

---

## 🚀 QUICK START: Render Deployment (RECOMMENDED)

### Step-by-Step:

```bash
# 1. Create GitHub repo and push code
cd ""
git init
git add .
git commit -m "SHL Assessment Recommendation System"

# Create repo on github.com, then:
git remote add origin YOUR_GITHUB_URL
git push -u origin main

# 2. Go to render.com
# - Sign up with GitHub
# - New Web Service
# - Connect your repo
# - Set build command: pip install -r requirements.txt
# - Set start command: python app.py
# - Add env var: GEMINI_API_KEY

# 3. Deploy! (automatic)
```

Your API will be live in 2-3 minutes at:
```
https://your-app-name.onrender.com
```

---

## Production Configuration

### Add to requirements.txt:
```txt
gunicorn==21.2.0  # Production server
```

### Create `Procfile` (for Heroku/Render):
```
web: gunicorn app:app
```

### Update app.py for production:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Use gunicorn in production, Flask dev server for local
    app.run(host='0.0.0.0', port=port)
```

---

## Environment Variables to Set

On your deployment platform, configure:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
PORT=5000
FLASK_ENV=production
```

---

## Testing Your Deployed API

```bash
# Replace with your actual URL
API_URL="https://your-app.onrender.com"

# Test health
curl $API_URL/health

# Test recommendation
curl -X POST $API_URL/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"Java developer with communication skills"}'
```

---

## Cost Comparison

| Platform | Free Tier | Limitations |
|----------|-----------|-------------|
| **Render** | ✅ Free forever | Sleeps after 15min inactive |
| **Railway** | $5/month credit | Limited hours |
| **Cloud Run** | 2M requests/month | Google Cloud account |
| **Heroku** | ❌ Requires credit card | 550 hours/month |
| **PythonAnywhere** | ✅ Free forever | Limited CPU |

**RECOMMENDATION**: Use **Render.com** for easiest free deployment.

---

## Frontend Deployment (Optional)

If you want to deploy just the frontend separately:

### Netlify/Vercel (FREE):
1. Upload `static/index.html` to Netlify
2. Update API_URL in the HTML to your deployed API URL
3. Done!

---

## Troubleshooting

### Issue: API not responding
**Solution**: Check logs on your platform dashboard

### Issue: 502 Bad Gateway
**Solution**: Ensure PORT environment variable is set

### Issue: Import errors
**Solution**: Verify requirements.txt includes all dependencies

---

## 📝 For Assignment Submission

Provide these URLs:
1. **API URL**: `https://your-app.onrender.com/recommend`
2. **Frontend URL**: `https://your-app.onrender.com/` (serves static/index.html)
3. **GitHub Code**: `https://github.com/YOUR_USERNAME/shl-assessment-recommender`

All three requirements satisfied with one Render deployment!
