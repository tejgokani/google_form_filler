# Deployment Guide for Google Form Filler### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build (Docker build + Playwright installation takes time)
3. Copy your backend URL (e.g., `https://form-filler-backend.onrender.com`)

⚠️ **Important Notes:**
- **Docker is recommended** for Playwright on Render (more stable than native build)
- First request may be slow (cold start on free tier)
- Render free tier sleeps after 15min inactivity
- Browser automation requires at least 512MB RAM
- **Upgrade to paid plan ($7/mo)** for better performance and no cold startsrerequisites
- GitHub account
- Vercel account (for frontend)
- Render account (for backend)
- Google Gemini API key (from https://aistudio.google.com/app/apikey)

---

## 🎯 Backend Deployment (Render)

### Step 1: Prepare Repository
1. Push your code to GitHub
2. Make sure `.env` is in `.gitignore` (don't commit secrets!)

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the **`gff/b`** directory (backend folder)

### Step 3: Configure Service
**Build Settings:**
- **Name**: `form-filler-backend` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main` (or your default branch)
- **Root Directory**: `gff/b`
- **Runtime**: `Docker` (⚠️ Important: Choose Docker, not Python!)
- **Dockerfile Path**: `gff/b/Dockerfile`

**Docker will auto-detect and use the Dockerfile**

**Environment Variables:**
Click **"Advanced"** and add:
- **Key**: `GEMINI_API_KEY`  
  **Value**: Your Gemini API key from https://aistudio.google.com/app/apikey
  
- **Key**: `ALLOWED_ORIGINS`  
  **Value**: `https://your-vercel-app.vercel.app` (update after frontend deployment)

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build (Playwright installation takes time)
3. Copy your backend URL (e.g., `https://form-filler-backend.onrender.com`)

⚠️ **Important Notes:**
- First request be slow (cold start on free tier)
- Render free tier sleeps after 15min inactivity
- Browser automation requires at least 512MB RAM

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Configure Environment
1. In your local `gff/f` folder, create `.env.production`:
   ```bash
   REACT_APP_API_URL=https://your-render-backend-url.onrender.com
   ```
   Replace with your actual Render backend URL from above

### Step 2: Deploy on Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `gff/f`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `build` (default)

### Step 3: Add Environment Variable
In Vercel project settings:
1. Go to **Settings** → **Environment Variables**
2. Add variable:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://your-render-backend-url.onrender.com`
   - **Environment**: All (Production, Preview, Development)

### Step 4: Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Copy your frontend URL (e.g., `https://form-filler.vercel.app`)

### Step 5: Update Backend CORS
1. Go back to Render dashboard
2. Open your backend service
3. Go to **Environment** tab
4. Update **`ALLOWED_ORIGINS`** variable:
   ```
   https://your-vercel-app.vercel.app,http://localhost:3000
   ```
5. Save changes (will trigger automatic redeploy)

---

## ✅ Verify Deployment

### Test Backend
```bash
curl https://your-backend.onrender.com
```
Should return connection info or 404 (means it's running)

### Test Frontend
1. Open your Vercel URL
2. Try filling a simple Google Form
3. Check browser console for errors

### Common Issues

**Backend Issues:**
- ❌ **"Module not found"**: Check `requirements.txt` has all dependencies
- ❌ **"Playwright install failed"**: Increase timeout or use `--with-deps chromium` flag
- ❌ **"CORS error"**: Update `ALLOWED_ORIGINS` in Render with correct Vercel URL
- ❌ **"Cold start timeout"**: First request after sleep may timeout, try again

**Frontend Issues:**
- ❌ **"Failed to fetch"**: Check `REACT_APP_API_URL` environment variable
- ❌ **"CORS error"**: Backend `ALLOWED_ORIGINS` must include frontend URL
- ❌ **"Empty responses"**: Check backend logs in Render dashboard

---

## 🔒 Security Checklist

- [ ] `.env` files are in `.gitignore`
- [ ] Gemini API key is only in Render environment variables
- [ ] CORS is configured with specific origins (not `*`)
- [ ] Backend timeout is set appropriately (300s)
- [ ] Rate limiting considered for production

---

## 📊 Monitoring

**Render:**
- View logs: Dashboard → Your Service → Logs tab
- Monitor usage: Dashboard → Account → Usage

**Vercel:**
- View logs: Project → Deployments → Click deployment → Functions tab
- Monitor: Project → Analytics

---

## 💰 Cost Considerations

**Free Tier Limits:**
- **Render**: 750 hours/month, sleeps after 15min inactivity
- **Vercel**: 100 GB bandwidth, 6000 build minutes/month

**Upgrade Triggers:**
- Heavy form submissions (>50/day)
- Large forms with many fields
- Need faster cold starts

---

## 🚀 Next Steps After Deployment

1. **Test thoroughly** with various Google Forms
2. **Monitor logs** for first week
3. **Set up alerts** in Render/Vercel
4. **Consider caching** for frequently used forms
5. **Add rate limiting** for production use

---

## 📞 Support

**Issues?**
- Check Render logs for backend errors
- Check browser console for frontend errors
- Verify environment variables are set correctly
- Test locally first to isolate deployment issues

**Resources:**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Playwright on Render: https://render.com/docs/deploy-playwright
