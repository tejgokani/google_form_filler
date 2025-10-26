# 🚀 Deployment Guide - Google Form Filler

## 📋 Pre-Deployment Checklist

### ✅ Fixed Issues:
- [x] Removed hardcoded API key from test_gemini.py (SECURITY FIX)
- [x] Updated test script to use HTTP approach (matching app.py)
- [x] Frontend already uses environment variable for API URL
- [x] Backend CORS configured for environment-based origins

### ⚠️ Required Actions Before Deployment:

#### 1. **CRITICAL: Secure Your API Key**
Your Gemini API key was found hardcoded in `test_gemini.py`. This has been fixed, but:
- ❌ **NEVER commit API keys to Git**
- ✅ **Always use environment variables**
- 🔒 **Regenerate your API key** from [Google AI Studio](https://makersuite.google.com/app/apikey) if it was committed

#### 2. **Backend Environment Variables**
Create a `.env` file in `/gff/b/` (already in .gitignore):
```bash
GEMINI_API_KEY=your-actual-api-key-here
GEMINI_MODEL=gemini-2.5-flash
PORT=5002
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

#### 3. **Frontend Environment Variables**
The frontend already reads from `process.env.REACT_APP_API_URL`, but you need to set it on Vercel.

---

## 🎯 Deployment Steps

### 1️⃣ Backend Deployment on Render

#### Step 1: Create Render Account
- Go to [Render.com](https://render.com)
- Sign up with GitHub

#### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `google-form-filler-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main` or `master`
   - **Root Directory**: `gff/b`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps
     ```
   - **Start Command**: 
     ```bash
     gunicorn app:app
     ```

#### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:
```
GEMINI_API_KEY=your-actual-api-key
GEMINI_MODEL=gemini-2.5-flash
PORT=5002
ALLOWED_ORIGINS=https://your-frontend.vercel.app
PYTHON_VERSION=3.11.0
```

#### Step 4: Advanced Settings
- **Plan**: Free (or Starter for better performance)
- **Health Check Path**: `/` (optional)
- **Auto-Deploy**: Yes

#### ⚠️ Important Render Notes:
1. **Playwright on Render**: The free tier may struggle with Playwright. Consider:
   - Upgrading to a paid plan ($7/month minimum)
   - Using Docker deployment (more stable)
   - Alternative: Deploy on Railway.app or Fly.io

2. **Expected Deploy Time**: 5-10 minutes (Playwright installation is slow)

3. **Copy your Render URL**: e.g., `https://google-form-filler-backend.onrender.com`

---

### 2️⃣ Frontend Deployment on Vercel

#### Step 1: Create Vercel Account
- Go to [Vercel.com](https://vercel.com)
- Sign up with GitHub

#### Step 2: Import Project
1. Click "Add New..." → "Project"
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `gff/f`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)

#### Step 3: Set Environment Variables
In Vercel project settings → Environment Variables:
```
REACT_APP_API_URL=https://google-form-filler-backend.onrender.com
```
Replace with your actual Render backend URL.

#### Step 4: Deploy
- Click "Deploy"
- Wait 1-2 minutes
- Copy your Vercel URL: e.g., `https://your-app.vercel.app`

#### Step 5: Update Backend CORS
Go back to Render and update `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## 🔧 Post-Deployment Configuration

### Update CORS on Backend
1. Go to Render dashboard
2. Edit `ALLOWED_ORIGINS` environment variable
3. Add your Vercel URL
4. Render will auto-redeploy

### Test the Integration
1. Visit your Vercel URL
2. Enter a test Google Form URL
3. Generate 1 response
4. Check if it works!

---

## 🧪 Testing

### Test Backend API (Before Frontend Deploy):
```bash
curl -X POST https://your-backend.onrender.com/generate \
  -H "Content-Type: application/json" \
  -d '{
    "formUrl": "https://docs.google.com/forms/...",
    "numResponses": 1,
    "intervalMinutes": 0,
    "intervalSeconds": 5,
    "formContext": "Test form",
    "responseTone": "neutral"
  }'
```

### Test Gemini API Locally:
```bash
cd gff/b
export GEMINI_API_KEY='your-key'
python test_gemini.py
```

---

## 📊 Current Project Status

### ✅ Ready for Deployment:
- ✅ Backend uses Google Gemini API (HTTP)
- ✅ Frontend uses environment variables
- ✅ CORS configured properly
- ✅ Indian name/email generation working
- ✅ Alternating pattern for unknown fields
- ✅ AI response generation with tone
- ✅ All Google Form field types supported
- ✅ Security: No hardcoded secrets

### ⚙️ Features:
- **AI-Powered Responses**: Context and tone-aware
- **Indian Identity**: Per-submission name/email generation
- **Smart Detection**: Handles all field types (text, textarea, radio, checkbox, grids)
- **Alternating Pattern**: Name → Email → Name for unclear fields
- **Custom Intervals**: User-defined delays between submissions
- **Beautiful UI**: Modern cyber-themed interface

---

## 🐛 Troubleshooting

### Issue: "Module not found" on Render
**Solution**: Check `requirements.txt` has all dependencies

### Issue: Playwright fails on Render Free Tier
**Solution**: 
1. Upgrade to Starter plan ($7/mo)
2. Or use Docker deployment
3. Or switch to Railway.app

### Issue: CORS errors in browser
**Solution**: 
1. Check `ALLOWED_ORIGINS` on Render includes your Vercel URL
2. Make sure URLs don't have trailing slashes

### Issue: Backend takes long to respond
**Solution**: 
- Render Free tier spins down after 15 min inactivity
- First request may take 30-60 seconds to wake up
- Consider upgrading to paid plan

### Issue: Form submission fails
**Solution**:
1. Check browser console for errors
2. Verify Google Form URL is accessible
3. Test with a simple 2-question form first
4. Check Render logs for backend errors

---

## 💰 Cost Estimate

### Free Tier (For Testing):
- **Vercel**: Free (hobby plan)
- **Render**: Free (with limitations)
- **Gemini API**: Free tier (60 requests/minute)
- **Total**: $0/month

### Recommended Production:
- **Vercel**: Free (hobby) or $20/month (Pro)
- **Render**: $7/month (Starter) - More stable for Playwright
- **Gemini API**: Free tier or $0.00025/1K chars (paid)
- **Total**: ~$7/month

---

## 📚 Alternative Deployment Options

### Railway.app (Recommended Alternative to Render)
- Better Playwright support
- $5/month minimum
- Easier configuration
- Better performance

### Fly.io
- Good for Playwright
- Pay-as-you-go
- More control
- Requires Docker knowledge

### Heroku
- Not recommended (no free tier)
- $7/month minimum
- Good Playwright support

---

## 🔐 Security Best Practices

1. **API Keys**: Always use environment variables
2. **CORS**: Only allow your frontend domain
3. **Rate Limiting**: Consider adding rate limits (not implemented yet)
4. **Input Validation**: Already implemented in backend
5. **HTTPS Only**: Vercel and Render provide this by default

---

## 📞 Support

If you encounter issues:
1. Check Render logs (Dashboard → Logs)
2. Check browser console (F12)
3. Review this guide
4. Test locally first with `python app.py`

---

## ✨ Next Steps (Optional Enhancements)

- [ ] Add rate limiting to prevent abuse
- [ ] Add user authentication
- [ ] Store submission history
- [ ] Add more AI tone options
- [ ] Support for file uploads in forms
- [ ] Retry logic for failed submissions
- [ ] Email notifications on completion
- [ ] Dashboard to track submissions

---

**Good luck with your deployment! 🚀**
