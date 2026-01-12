# 🚀 LEGID - Quick Start Guide

## ⚡ Start in 3 Steps

### 1️⃣ Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2️⃣ Start Frontend Server
Open a **NEW terminal** window:
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3️⃣ Open in Browser
Navigate to: **http://localhost:5173**

---

## 🎯 User Journey

### Step 1: Select Language
Choose from:
- 🇬🇧 English
- 🇫🇷 French  
- 🇪🇸 Spanish

Click **"+ More Options"** for:
- 🇮🇳 Hindi
- 🇮🇳 Punjabi
- 🇨🇳 Chinese

### Step 2: Select Country
- 🇨🇦 Canada
- 🇺🇸 United States

### Step 3: Select Province/State
**Canada:** Ontario, BC, Alberta, Quebec, etc.
**USA:** California, Texas, New York, Florida, etc.

### Step 4: Select Law Type
Choose from 14+ categories:
- Criminal Law
- Traffic Law
- Immigration Law
- Family Law
- Employment Law
- Business Law
- Real Estate Law
- And more...

### Step 5: Ask Questions!
Start chatting with LEGID about your legal questions.

---

## 💡 Example Questions to Try

### Immigration Law
```
"What are the requirements for Express Entry to Canada?"
"How do I apply for a work permit in Ontario?"
"What is the processing time for permanent residence?"
```

### Criminal Law
```
"What are the penalties for theft under $5000 in Ontario?"
"What happens if I'm charged with assault?"
"What are my rights when arrested?"
```

### Traffic Law
```
"What are the penalties for distracted driving in Ontario?"
"How many demerit points for speeding 30 km/h over?"
"Can I fight a red light camera ticket?"
```

### Employment Law
```
"What is wrongful dismissal in Ontario?"
"How much notice am I entitled to if fired?"
"What are my rights regarding overtime pay?"
```

### Family Law
```
"How is child support calculated in Ontario?"
"What are the grounds for divorce in Canada?"
"How is property divided in a divorce?"
```

---

## 📤 Upload Documents

You can upload legal documents for analysis:

### Supported Formats
- **PDF** - Legal documents, court papers
- **Images** (JPG, PNG) - Photos of documents (OCR enabled)
- **Word** (DOCX) - Contracts, agreements
- **Text** (TXT) - Plain text documents

### How to Upload
1. **Drag & Drop** - Drag files into the chat window
2. **Paste** - Press `Ctrl+V` to paste from clipboard
3. **Click** - Click the upload button and select files

### What Happens
- Text is extracted (including OCR for images)
- Document is analyzed
- LEGID answers questions based on the document content

---

## 🎤 Voice Features

### Voice Input
1. Click the microphone button
2. Speak your question
3. LEGID will transcribe and answer

### Text-to-Speech
1. Toggle "Auto-read responses"
2. LEGID will read answers aloud
3. Or click the speaker icon on any message

---

## 🔄 Recent Updates

Click **"Recent Updates"** to see:
- Latest legal changes
- New court decisions
- Policy updates
- Legislative amendments

All updates include:
- Date and effective date
- Summary of changes
- Official source links
- Jurisdiction

---

## 🌐 Government Resources

Click **"Government Resources"** for quick access to:

### Canada
- Justice Canada
- Immigration Canada (IRCC)
- Canada Revenue Agency (CRA)
- Provincial government sites

### USA
- Congress.gov
- USCIS (Immigration)
- IRS (Tax)
- State government sites

---

## ⚙️ Settings

### Change Language
Click your current language in the header to switch

### Change Country/Province
Click your location in the header to change

### Change Law Type
Click "Change Law Type" to select a different legal area

### Start New Chat
Click "New Chat" to begin a fresh conversation

### Generate Summary
After a conversation, click "Generate Summary" to create a case summary

---

## 🎨 Interface Features

### Dark Theme
- Modern dark gradient background
- Cyan accent colors
- Glassmorphism effects
- Smooth animations

### LEGID Logo
- Fancy white text with glow
- Shimmer animation
- Consistent across all pages

### Responsive Design
- Works on desktop, tablet, mobile
- Adaptive layouts
- Touch-friendly controls

---

## 📋 Response Format

Every LEGID response includes:

1. **Introduction** - Brief summary
2. **Direct Answer** - Clear answer to your question
3. **Legal Basis** - Statutes, codes, sections cited
4. **Detailed Explanation** - How the law applies
5. **Jurisdiction Context** - Specific to your location
6. **Key Details** - Important dates, requirements
7. **Case Study** - Real court cases cited
8. **Real-Time Updates** - Recent changes
9. **Sources** - Official government links
10. **Next Steps** - What to do next
11. **Disclaimer** - Legal disclaimer

---

## 🆘 Troubleshooting

### Backend Won't Start
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Check Python version (need 3.8+)
python --version

# Try running directly
python -m uvicorn app.main:app --reload
```

### Frontend Won't Start
```bash
# Install dependencies
cd frontend
npm install

# Clear cache
npm cache clean --force

# Try again
npm run dev
```

### Port Already in Use
```bash
# Backend (change port)
python -m uvicorn app.main:app --reload --port 8001

# Frontend (change port in vite.config.js)
```

### Can't Connect to Backend
- Make sure backend is running on port 8000
- Check `http://localhost:8000/docs` in browser
- Verify no firewall blocking

---

## 🎯 Pro Tips

### 1. Be Specific
❌ "Tell me about criminal law"
✅ "What are the penalties for theft under $5000 in Ontario?"

### 2. Include Details
❌ "What happens if I speed?"
✅ "What are the penalties for speeding 40 km/h over the limit in Ontario?"

### 3. Mention Your Jurisdiction
❌ "How do I get a work permit?"
✅ "How do I apply for a work permit in Ontario, Canada?"

### 4. Ask Follow-Up Questions
- LEGID remembers your conversation
- Ask for clarification
- Request more details on specific points

### 5. Upload Relevant Documents
- Upload tickets, notices, contracts
- LEGID will analyze and explain them
- Get specific advice based on your documents

---

## 📊 What LEGID Can Do

✅ **Answer Legal Questions** - Comprehensive, cited responses
✅ **Cite Sources** - Official government websites
✅ **Reference Cases** - Real court decisions
✅ **Track Updates** - Latest legal changes
✅ **Analyze Documents** - Upload and get explanations
✅ **Multiple Languages** - 6 languages supported
✅ **Voice Interaction** - Speak and listen
✅ **Jurisdiction-Specific** - Tailored to your location

---

## ❌ What LEGID Cannot Do

❌ **Provide Legal Advice** - Only general information
❌ **Represent You** - Not a lawyer
❌ **Guarantee Outcomes** - Every case is different
❌ **Replace Lawyers** - Consult professionals for your case

---

## 📞 Need Help?

### Documentation
- `LEGID_IMPLEMENTATION_SUMMARY.md` - Full system overview
- `frontend/README.md` - Frontend documentation
- `backend/README.md` - Backend documentation

### API Documentation
- Visit `http://localhost:8000/docs` when backend is running
- Interactive API explorer
- Test endpoints directly

### Example Responses
- Try the example questions above
- Explore different law types
- Upload sample documents

---

## 🎉 You're Ready!

Start using LEGID to get professional legal information with:
- ⚖️ Proper citations
- 📚 Case studies
- 🔄 Real-time updates
- 🌐 Official sources
- 🎯 Jurisdiction-specific answers

**Remember:** LEGID provides legal information, not legal advice. Always consult a licensed lawyer for your specific situation.

---

**Enjoy using LEGID! 🚀**
