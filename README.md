# 🤖 Google Form Filler - AI-Powered Response Generator

Intelligent automation tool for Google Forms with AI-powered context-aware responses, smart field detection, and Indian identity generation.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![React](https://img.shields.io/badge/react-19.1-blue)

---

## ✨ Features

### 🎯 Core Capabilities
- **AI-Powered Responses**: Google Gemini integration for intelligent, context-aware answers
- **Smart Field Detection**: Automatically identifies name, email, phone, address fields
- **Indian Identity Generation**: Creates realistic Indian names with derived emails per submission
- **Tone Control**: Positive, Negative, Neutral, or Mixed response tones
- **All Question Types**: Text, textarea, radio, checkbox, dropdowns, linear scales, grids
- **Batch Processing**: Submit 1-50 responses with customizable intervals (1s - 5min)
- **Auto-Submit**: Automatically submits forms after filling

### 🧠 Intelligent Features
- **Alternating Pattern**: When field labels are unclear, intelligently alternates between name/email
- **Context Awareness**: Analyzes form context for relevant, meaningful responses
- **Grid Intelligence**: Detects and fills mixed grids with name/email columns
- **Email Priority**: Prioritizes email detection to prevent filling random text
- **Graceful Fallback**: Works even when AI is unavailable with smart templated responses

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API key ([Get one free](https://makersuite.google.com/app/apikey))

### 1. Backend Setup
```bash
# Navigate to backend
cd gff/b

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your-api-key-here

# Run backend
python app.py
# Backend runs on http://127.0.0.1:5002
```

### 2. Frontend Setup
```bash
# Navigate to frontend
cd gff/f

# Install dependencies
npm install

# Run frontend
npm start
# Frontend opens at http://localhost:3000
```

### 3. Test
1. Open http://localhost:3000
2. Enter a Google Form URL
3. Set number of responses and interval
4. Click "INITIATE GENERATION"
5. Watch the magic! ✨

---

## 🎮 How to Use

### Basic Usage
1. **Enter Form URL**: Paste your Google Form link
2. **Set Response Count**: Choose 1-50 submissions
3. **Configure Interval**: Set delay between submissions (default: 5 seconds)
4. **Click Generate**: Watch automation fill and submit forms

### Advanced Options (Optional)
- **Form Context**: Describe the form topic (e.g., "Movie feedback survey") for better AI responses
- **Response Tone**: 
  - 😊 **Positive**: Enthusiastic, satisfied responses
  - 😐 **Neutral**: Balanced, objective responses
  - 😞 **Negative**: Critical, dissatisfied responses
  - 🤔 **Mixed**: Combination of positive and negative

---

## 📦 Deployment

### Backend (Render.com)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Create Web Service on Render**
   - Go to [render.com](https://render.com) → New Web Service
   - Connect your GitHub repository
   - **Settings:**
     ```
     Name: form-filler-backend
     Root Directory: gff/b
     Build Command: pip install -r requirements.txt && playwright install chromium && playwright install-deps
     Start Command: gunicorn app:app
     ```

3. **Add Environment Variables**
   ```
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-2.5-flash
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   ```

4. Deploy and copy your backend URL

### Frontend (Vercel.com)

1. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com) → New Project
   - Import your GitHub repository
   - **Settings:**
     ```
     Framework: Create React App
     Root Directory: gff/f
     Build Command: npm run build
     Output Directory: build
     ```

2. **Add Environment Variable**
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com
   ```

3. **Update Backend CORS**
   - Go back to Render
   - Update `ALLOWED_ORIGINS` with your Vercel URL

---

## 🏗️ Project Structure

```
gff/
├── b/                          # Backend (Flask + Playwright)
│   ├── app.py                  # Main application
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile               # Render deployment config
│   ├── render-service.yaml    # Render service config
│   ├── test_gemini.py         # API test script
│   └── .env.example           # Environment template
│
├── f/                          # Frontend (React)
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── App.css            # Cyberpunk styling
│   │   └── index.js           # Entry point
│   ├── package.json           # Node dependencies
│   └── public/                # Static assets
│
└── README.md                  # This file
```

---

## 🔧 Configuration

### Backend Environment Variables (.env)
```bash
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
PORT=5002
```

### Frontend Environment Variables
**Local (.env.local)**
```bash
REACT_APP_API_URL=http://127.0.0.1:5002
```

**Production (Vercel)**
```bash
REACT_APP_API_URL=https://your-backend.onrender.com
```

---

## �� Supported Google Form Types

| Question Type | Status | Notes |
|--------------|--------|-------|
| Short Answer | ✅ | Smart field detection (name/email/phone/address/city) |
| Paragraph | ✅ | AI-generated context-aware responses |
| Multiple Choice | ✅ | Random selection |
| Checkboxes | ✅ | Selects 1-3 random options |
| Dropdown | ✅ | Random selection |
| Linear Scale | ✅ | Weighted towards middle-high ratings |
| Multiple Choice Grid | ✅ | Random selection per row |
| Checkbox Grid | ✅ | 1-2 selections per row |
| Text Grid | ✅ | Smart name/email column detection |
| Date/Time | ⚠️ | Not yet implemented |
| File Upload | ❌ | Not supported |

---

## 🧪 Testing

### Test Gemini API
```bash
cd gff/b
export GEMINI_API_KEY='your-key'
python test_gemini.py
```

### Test Locally
1. Start backend: `cd gff/b && python app.py`
2. Start frontend: `cd gff/f && npm start`
3. Open http://localhost:3000
4. Test with a simple 2-question form

---

## 🐛 Troubleshooting

### Backend Issues

**"Module not found"**
- Solution: Activate venv and run `pip install -r requirements.txt`

**"Playwright not found"**
- Solution: Run `playwright install chromium`

**"CORS error"**
- Solution: Check `ALLOWED_ORIGINS` includes your frontend URL

**"Gemini API error"**
- Solution: Verify `GEMINI_API_KEY` is set and valid

### Frontend Issues

**"Failed to fetch"**
- Solution: Check backend is running and `REACT_APP_API_URL` is correct

**"CORS blocked"**
- Solution: Backend CORS must allow frontend origin

### Form Filling Issues

**Fields not filling**
- Check browser console for errors
- Verify form is publicly accessible
- Test with a simpler form first

**Wrong data in fields**
- Review backend terminal logs
- Check field detection logic

**Form not submitting**
- Some forms may have custom validation
- Check for required fields

---

## 🔒 Security & Best Practices

### ⚠️ Important Warnings
- **Use Responsibly**: Don't abuse Google Forms or spam surveys
- **Respect Privacy**: Don't collect or store sensitive user data
- **API Limits**: Monitor Gemini API usage (free tier: 60 requests/min)
- **Terms of Service**: Ensure compliance with Google Forms TOS

### Security Measures
- ✅ API keys in environment variables only
- ✅ CORS configured for specific origins
- ✅ No sensitive data in code
- ✅ `.env` files gitignored
- ✅ Input validation on backend

---

## 💰 Cost Estimate

### Free Tier (Development/Testing)
- **Vercel**: Free (Hobby plan)
- **Render**: Free (with cold starts)
- **Gemini API**: Free tier (60 req/min)
- **Total**: $0/month

### Production (Recommended)
- **Vercel**: Free or $20/month (Pro)
- **Render**: $7/month (Starter) - Better for Playwright
- **Gemini API**: Free tier or paid ($0.00025/1K chars)
- **Total**: ~$7/month

---

## 🎯 Key Technical Details

### Smart Field Detection
The app uses multiple methods to identify field types:
1. Checks aria-label attributes
2. Analyzes placeholder text
3. Examines parent question text
4. Matches against keyword patterns
5. Falls back to alternating name/email pattern

### AI Response Generation
- Uses Google Gemini 2.5 Flash model
- HTTP-based API calls (no SDK dependencies)
- Context-aware prompt engineering
- Tone-specific response templates
- Graceful fallback for API failures

### Identity Generation
- Uses Faker library with Indian locale ('en_IN')
- Generates: first name, last name, full name
- Derives email from name (e.g., raj.sharma42@gmail.com)
- Consistent identity per submission

---

## 🤝 Contributing

Contributions welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - Use at your own risk. This tool is for educational and testing purposes only.

---

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered response generation
- **Playwright**: Reliable browser automation
- **Faker**: Realistic data generation
- **Flask**: Lightweight backend framework
- **React**: Modern frontend library

---

## 📞 Support

### Common Questions

**Q: Can I use this for production surveys?**
A: This tool is designed for testing. Use responsibly and only on forms you own or have permission to test.

**Q: Why is the first request slow on Render?**
A: Render free tier spins down after 15 minutes of inactivity. Consider upgrading to paid tier for faster response.

**Q: Can I add more field types?**
A: Yes! Extend the field detection logic in `app.py` around line 360-470.

**Q: How do I add rate limiting?**
A: Consider using Flask-Limiter or implementing custom rate limiting logic.

### Need Help?
- Check browser console (F12) for frontend errors
- Check Render logs for backend errors
- Verify environment variables are set
- Test locally first to isolate issues

---

## 🔄 Changelog

### v2.0 (Current)
- ✅ Migrated from OpenAI to Google Gemini
- ✅ Added Indian name/email generation
- ✅ Implemented smart alternating pattern
- ✅ Enhanced grid column detection
- ✅ Added context-aware AI responses
- ✅ Implemented tone control
- ✅ Improved field detection
- ✅ Production-ready configuration
- ✅ Comprehensive documentation

### v1.0
- Basic form filling
- OpenAI integration
- Simple field detection

---

## 🚧 Future Enhancements

- [ ] Add rate limiting
- [ ] Support for date/time fields
- [ ] User authentication
- [ ] Submission history dashboard
- [ ] Email notifications
- [ ] Retry logic for failed submissions
- [ ] Support for conditional questions
- [ ] Multi-language support
- [ ] Webhook integrations

---

**Made with ❤️ for automating boring tasks**

⚡ **Happy Automating!** ⚡
