# ⚡ Quick Deploy Checklist

## 🚨 CRITICAL FIRST STEP
**Your API key was exposed in test_gemini.py** - It has been removed, but you should:
```bash
# Regenerate your API key at:
https://makersuite.google.com/app/apikey
```

---

## 📦 Backend (Render.com)

### 1. Push to GitHub (if not already)
```bash
cd "/Users/tejgokani/Desktop/form filler/gff"
git init
git add .
git commit -m "Initial commit - ready for deployment"
git remote add origin https://github.com/yourusername/form-filler.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) → New Web Service
2. Connect GitHub repo
3. **Settings:**
   ```
   Name: form-filler-backend
   Root Directory: gff/b
   Build Command: pip install -r requirements.txt && playwright install chromium && playwright install-deps
   Start Command: gunicorn app:app
   ```
4. **Environment Variables:**
   ```
   GEMINI_API_KEY=your-new-api-key
   GEMINI_MODEL=gemini-2.5-flash
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
5. Click "Create Web Service"
6. ⏱️ Wait 5-10 minutes
7. 📋 **Copy your backend URL**

---

## 🎨 Frontend (Vercel.com)

### 1. Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. **Settings:**
   ```
   Framework: Create React App
   Root Directory: gff/f
   Build Command: npm run build
   Output Directory: build
   ```
4. **Environment Variable:**
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```
   (Use the URL from Render step 7)
5. Click "Deploy"
6. ⏱️ Wait 1-2 minutes
7. 📋 **Copy your frontend URL**

### 2. Update Backend CORS
Go back to Render → Environment Variables → Edit `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## ✅ Test

Visit: `https://your-app.vercel.app`

Enter a test form URL and generate 1 response!

---

## 🐛 If Something Breaks

### Backend won't start:
- Check Render logs
- Verify `GEMINI_API_KEY` is set
- Ensure Playwright installed (see build logs)

### Frontend can't connect:
- Check browser console (F12)
- Verify `REACT_APP_API_URL` on Vercel
- Check CORS in Render environment variables

### Form submission fails:
- Test with a simple 2-question form first
- Check Render logs for errors
- Ensure Google Form is public/accessible

---

## 💡 Pro Tips

- **First Request Slow**: Render free tier sleeps after 15 min → upgrade to $7/month
- **Test Locally First**: `cd gff/b && python app.py`
- **Use Railway.app**: Better alternative to Render for Playwright ($5/mo)

---

**Need help? Check DEPLOYMENT_GUIDE.md for detailed instructions!**
