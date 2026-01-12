# 🚀 Quick Voice Test Guide

**Quick reference for testing voice models in all languages**

---

## ⚡ Quick Start (3 Steps)

### 1. Run Diagnostic
```bash
cd legal-bot
python tests/diagnose_punjabi_voice.py
```

### 2. Open Browser Test
```bash
python tests/run_voice_tests.py browser
```

### 3. Test in Application
1. Open http://localhost:4200 (or your app URL)
2. Select Punjabi language
3. Click microphone button
4. Speak: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ"

---

## 🎯 Test Commands

| Command | Purpose |
|---------|---------|
| `python tests/diagnose_punjabi_voice.py` | Check Punjabi configuration |
| `python tests/run_voice_tests.py` | Run all tests |
| `python tests/run_voice_tests.py browser` | Open browser test page |
| `pytest tests/test_voice_all_languages.py -v` | Run automated tests |
| `python tests/test_voice_all_languages.py` | Show configuration |

---

## 🔍 Quick Checks

### Is Punjabi Configured?
```bash
# Should show: ✅ Punjabi TTS voice mapping found: 'pa' -> 'onyx'
python tests/diagnose_punjabi_voice.py
```

### Are All Languages Working?
```bash
# Should show: 36 passed
pytest tests/test_voice_all_languages.py -v
```

### Browser Voice Available?
Open browser console (F12) and run:
```javascript
speechSynthesis.getVoices().filter(v => v.lang.startsWith('pa'))
```

---

## 🎤 Test Punjabi Voice

### In Browser Console (F12)
```javascript
// Test TTS
const text = 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ';
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = 'pa-IN';
speechSynthesis.speak(utterance);

// Test STT
const recognition = new webkitSpeechRecognition();
recognition.lang = 'pa-IN';
recognition.onresult = (e) => console.log(e.results[0][0].transcript);
recognition.start();
```

### In Application
1. Go to http://localhost:4200
2. Click "Language: English" → Select "Punjabi ਪੰਜਾਬੀ"
3. Click microphone button 🎤
4. Speak in Punjabi
5. Bot responds in Punjabi

---

## 📊 Expected Results

### Diagnostic Output
```
✅ Backend Configuration:  PASS
✅ Frontend Configuration: PASS
✅ Text Encoding:          PASS
```

### Browser Test
- Click "Test TTS" → Hear Punjabi voice
- Click "Test STT" → Speak and see transcript
- All 6 languages show green ✅

### Application Test
- Microphone button appears
- Voice recording works
- Punjabi text transcribed
- Bot responds in Punjabi
- Andy reads response aloud

---

## 🐛 Quick Fixes

### Issue: No Punjabi Voice
**Fix:**
```
Chrome: chrome://settings/languages → Add Punjabi
Firefox: Install OS language pack
Safari: System Preferences → Speech → Download Punjabi
```

### Issue: Microphone Not Working
**Fix:**
```
1. Click lock icon in address bar
2. Allow microphone access
3. Reload page
```

### Issue: API Key Error
**Fix:**
```bash
# Windows
set OPENAI_API_KEY=your-key-here

# Linux/Mac
export OPENAI_API_KEY='your-key-here'
```

---

## 📱 Test on Different Browsers

| Browser | Command | Expected |
|---------|---------|----------|
| Chrome | Open test page | ✅ Full support |
| Edge | Open test page | ✅ Full support |
| Firefox | Open test page | ✅ Uses system voices |
| Safari | Open test page | ✅ macOS/iOS only |

---

## 🎯 Punjabi Test Phrases

Use these to test Punjabi voice:

| Phrase | Translation |
|--------|-------------|
| ਸਤ ਸ੍ਰੀ ਅਕਾਲ | Hello (Sikh greeting) |
| ਮੈਨੂੰ ਮਦਦ ਚਾਹੀਦੀ ਹੈ | I need help |
| ਕਾਨੂੰਨੀ ਸਲਾਹ | Legal advice |
| ਧੰਨਵਾਦ | Thank you |

---

## ✅ Success Checklist

- [ ] Diagnostic shows all ✅
- [ ] Browser test page opens
- [ ] Can hear Punjabi TTS
- [ ] Can use Punjabi STT
- [ ] Application microphone works
- [ ] Bot responds in Punjabi

---

## 📞 Need Help?

1. **Check diagnostic:** `python tests/diagnose_punjabi_voice.py`
2. **Read full docs:** `VOICE_MODELS_DOCUMENTATION.md`
3. **See test results:** `VOICE_TEST_RESULTS.md`
4. **Check browser console:** Press F12, look for errors

---

## 🎉 All Working?

If all checks pass:
- ✅ Punjabi voice is configured correctly
- ✅ All 6 languages are working
- ✅ Ready for production use

**Test with real users and gather feedback!**

---

**Quick Links:**
- [Full Documentation](VOICE_MODELS_DOCUMENTATION.md)
- [Test Results](VOICE_TEST_RESULTS.md)
- [Test Suite README](tests/README.md)
