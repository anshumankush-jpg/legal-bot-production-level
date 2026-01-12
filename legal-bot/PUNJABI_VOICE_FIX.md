# 🔧 Punjabi Voice Not Responding - Fix Guide

**Issue:** Punjabi voice is using "Default voice" instead of Punjabi-specific voice

**Root Cause:** Your browser doesn't have Punjabi voices installed

---

## 🎯 Quick Diagnosis

From your screenshot, I can see:
- ✅ Configuration is correct (Code: `pa`, STT: `pa-IN`, TTS Voice: `onyx`)
- ✅ Test text is in Punjabi (ਸਤ ਸ੍ਰੀ ਅਕਾਲ...)
- ❌ **Browser is using "Default voice"** instead of Punjabi voice

This means: **Your browser doesn't have Punjabi voices installed**

---

## 🔍 Check What Voices You Have

**I just opened a voice checker page in your browser.** It will show:
- How many voices are installed
- If Punjabi voices are available
- Instructions to install them

Look for:
- **"✅ Punjabi Voices Found!"** - Good, you have them
- **"❌ No Punjabi Voices Found"** - Need to install

---

## 🛠️ Solution 1: Install Punjabi Voice (FREE, Recommended)

### For Windows 10/11:

**Step 1: Install Punjabi Language**
1. Press `Win + I` to open Settings
2. Go to **Time & Language** → **Language**
3. Click **"Add a language"**
4. Search for **"Punjabi"** or type **"pa"**
5. Select **"Punjabi (India)"** or **"ਪੰਜਾਬੀ (ਭਾਰਤ)"**
6. Click **"Install"**
7. Wait for installation to complete

**Step 2: Install Speech Pack**
1. In Language settings, click on **Punjabi**
2. Click **"Options"**
3. Under **Speech**, click **"Download"**
4. Wait for speech pack to download and install

**Step 3: Restart Browser**
1. Close all browser windows
2. Reopen browser
3. Test again

### For Chrome/Edge (Alternative):

1. Open new tab and go to: `chrome://settings/languages`
2. Click **"Add languages"**
3. Search for **"Punjabi"**
4. Select **"Punjabi (India)"** and click **"Add"**
5. Click the 3 dots next to Punjabi
6. Check **"Offer to translate"**
7. Restart browser

---

## 🛠️ Solution 2: Use OpenAI TTS (High Quality, Costs Money)

Your backend is already configured to use OpenAI's `onyx` voice for Punjabi. This is **higher quality** and works on **all devices**.

### Setup:

**Step 1: Set API Key**

**PowerShell:**
```powershell
$env:OPENAI_API_KEY='your-api-key-here'
```

**CMD:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Step 2: Test It**
```bash
cd legal-bot
python tests/test_punjabi_openai.py
```

This will:
- Test Punjabi with OpenAI TTS
- Generate an MP3 file
- Play it automatically
- Show if it's working

**Step 3: Use in Production**

Just make sure `OPENAI_API_KEY` is set when running the backend server. The code already uses OpenAI TTS automatically.

---

## 🧪 Test Files Created

I've created these tools to help you:

### 1. Browser Voice Checker
**File:** `tests/check_browser_voices.html` (**JUST OPENED**)

Shows:
- All voices in your browser
- If Punjabi is available
- How to install it

### 2. OpenAI TTS Tester
**File:** `tests/test_punjabi_openai.py`

**Run:**
```bash
python tests/test_punjabi_openai.py
```

Tests Punjabi with OpenAI TTS and generates audio file.

---

## 📊 Comparison

| Method | Quality | Cost | Setup | Works Offline |
|--------|---------|------|-------|---------------|
| **Browser TTS** | Medium | FREE | Need to install | ✅ Yes |
| **OpenAI TTS** | High | ~$0.015/1K chars | Just API key | ❌ No |

---

## ✅ Verification Steps

### After Installing Punjabi Voice:

1. **Check voice checker page** (just opened)
   - Should show "✅ Punjabi Voices Found!"
   - Should list voice names like "Google ਪੰਜਾਬੀ"

2. **Test in original page**
   - Go back to the test page
   - Click "Test TTS" for Punjabi
   - Should now say "TTS Success! Used: Google ਪੰਜਾਬੀ" (or similar)

3. **Test in application**
   - Open http://localhost:4200
   - Select Punjabi language
   - Click microphone button
   - Speak and listen to response

---

## 🎯 Expected Results

### Before Fix:
```
TTS Success! Used: Default voice  ❌
```

### After Fix (Browser TTS):
```
TTS Success! Used: Google ਪੰਜਾਬੀ  ✅
```

### After Fix (OpenAI TTS):
```
TTS Success! Generated 15234 bytes  ✅
Voice: onyx (OpenAI)
```

---

## 🐛 Troubleshooting

### Issue: Still using default voice after installing

**Try:**
1. Restart browser completely (close ALL windows)
2. Clear browser cache
3. Reload the test page
4. Check voice checker to confirm Punjabi is there

### Issue: Can't find Punjabi in Windows settings

**Try:**
1. Update Windows (Settings → Update & Security)
2. Search for "ਪੰਜਾਬੀ" instead of "Punjabi"
3. Try "Punjabi (India)" or "Punjabi (Pakistan)"

### Issue: OpenAI test fails

**Check:**
1. API key is correct (starts with `sk-`)
2. API key has credits
3. OpenAI library installed: `pip install openai`
4. Internet connection working

---

## 📞 Quick Commands

```bash
# Check what voices you have (browser)
# Open: tests/check_browser_voices.html

# Test OpenAI TTS
python tests/test_punjabi_openai.py

# Run full diagnostic
python tests/diagnose_punjabi_voice.py

# Test all languages
python tests/run_voice_tests.py browser
```

---

## 💡 Recommendation

**For Development/Testing:**
- Use browser TTS (FREE)
- Install Punjabi voice on your machine

**For Production:**
- Use OpenAI TTS (better quality)
- Set `OPENAI_API_KEY` environment variable
- Backend already configured to use `onyx` voice

---

## 🎉 Summary

**Problem:** Browser doesn't have Punjabi voice installed

**Solution 1 (FREE):** Install Punjabi language pack in Windows + browser

**Solution 2 (Paid):** Use OpenAI TTS (already configured in backend)

**Status:** Configuration is ✅ correct, just need to install voice or use OpenAI

---

**Next Steps:**
1. Check the voice checker page I just opened
2. If no Punjabi voices, follow installation steps above
3. Test again
4. If still issues, use OpenAI TTS

**Need help?** Run: `python tests/diagnose_punjabi_voice.py`
