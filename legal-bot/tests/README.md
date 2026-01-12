# 🧪 Voice Model Tests

This directory contains comprehensive test suites for all voice models in the LEGID Legal Assistant.

## 📁 Files

### Test Files

| File | Purpose | Usage |
|------|---------|-------|
| `test_voice_all_languages.py` | Automated tests for all 6 languages | `pytest test_voice_all_languages.py -v` |
| `test_voice_browser.html` | Interactive browser test page | Open in browser |
| `diagnose_punjabi_voice.py` | Punjabi-specific diagnostic tool | `python diagnose_punjabi_voice.py` |
| `run_voice_tests.py` | Test runner for all voice tests | `python run_voice_tests.py` |

### Generated Files (after running tests)

- `punjabi_test_output.mp3` - Sample Punjabi audio from TTS test
- `punjabi_browser_test.js` - Browser console test code

---

## 🚀 Quick Start

### 1. Run All Tests

```bash
python run_voice_tests.py
```

This will:
- Check voice configuration
- Run automated tests
- Open browser test page

### 2. Test Specific Language (Punjabi)

```bash
python diagnose_punjabi_voice.py
```

This will:
- Check backend configuration
- Check frontend configuration
- Test OpenAI API
- Generate browser test code
- Provide recommendations

### 3. Browser Testing

```bash
python run_voice_tests.py browser
```

Opens interactive test page where you can:
- Test STT (Speech-to-Text) for each language
- Test TTS (Text-to-Speech) for each language
- See real-time results
- Track pass/fail statistics

---

## 📋 Supported Languages

All tests cover these 6 languages:

| Language | Code | TTS Voice | STT Code | Status |
|----------|------|-----------|----------|--------|
| English | `en` | `alloy` | `en-US` | ✅ |
| Hindi | `hi` | `nova` | `hi-IN` | ✅ |
| French | `fr` | `shimmer` | `fr-FR` | ✅ |
| Spanish | `es` | `fable` | `es-ES` | ✅ |
| **Punjabi** | `pa` | `onyx` | `pa-IN` | ✅ |
| Chinese | `zh` | `echo` | `zh-CN` | ✅ |

---

## 🔧 Setup

### Prerequisites

```bash
# Install Python dependencies
pip install pytest pytest-asyncio openai

# Set OpenAI API key (for TTS tests)
export OPENAI_API_KEY='your-key-here'  # Linux/Mac
set OPENAI_API_KEY=your-key-here       # Windows
```

### Browser Requirements

- **Chrome/Edge:** Best support for all languages
- **Firefox:** Good support, uses system voices
- **Safari:** Good support on macOS/iOS

---

## 📖 Test Details

### Automated Tests (`test_voice_all_languages.py`)

**Test Coverage:**
- ✅ Voice mapping verification
- ✅ TTS API calls
- ✅ STT language codes
- ✅ Browser voice preferences
- ✅ Error handling
- ✅ Punjabi-specific tests

**Run Options:**

```bash
# All tests
pytest test_voice_all_languages.py -v

# Specific test
pytest test_voice_all_languages.py -v -k "test_punjabi"

# With coverage
pytest test_voice_all_languages.py --cov

# Configuration check only
python test_voice_all_languages.py
```

### Browser Tests (`test_voice_browser.html`)

**Features:**
- Visual test interface
- Real-time audio visualization
- Test result tracking
- Individual or batch testing

**How to Use:**
1. Open `test_voice_browser.html` in browser
2. Click "Test All Languages" or test individually
3. For STT: Click "Test STT" and speak when prompted
4. For TTS: Click "Test TTS" to hear the voice

### Punjabi Diagnostic (`diagnose_punjabi_voice.py`)

**What It Checks:**
1. Backend configuration (OpenAI TTS)
2. Frontend configuration (Browser STT/TTS)
3. OpenAI API key validity
4. Punjabi TTS functionality
5. Text encoding (Gurmukhi script)
6. Browser voice availability

**Output:**
- Detailed diagnostic report
- Generated audio sample (if API key present)
- Browser test code
- Recommendations for fixes

---

## 🐛 Troubleshooting

### Issue: Punjabi Voice Not Working

**Diagnosis:**
```bash
python diagnose_punjabi_voice.py
```

**Common Causes:**

1. **Browser doesn't have Punjabi voice**
   - Solution: Install Punjabi language pack
   - Chrome: `chrome://settings/languages`
   - Firefox: Install OS language pack
   - Safari: System Preferences > Speech

2. **OpenAI API key not set**
   - Solution: Set `OPENAI_API_KEY` environment variable
   - Backend TTS requires this

3. **Microphone permissions**
   - Solution: Allow microphone access in browser
   - Check browser settings

4. **Text encoding issues**
   - Solution: Ensure UTF-8 encoding
   - Test with diagnostic tool

### Issue: Tests Failing

**Check:**
```bash
# Verify configuration
python test_voice_all_languages.py

# Check specific language
pytest test_voice_all_languages.py -v -k "punjabi"

# Run with verbose output
pytest test_voice_all_languages.py -vv
```

### Issue: No Audio Output

**Check:**
1. Volume settings
2. Audio output device
3. Browser audio permissions
4. OpenAI API key (for backend TTS)

---

## 📊 Test Results

### Expected Results

**All tests passing:**
```
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[en] PASSED
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[hi] PASSED
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[fr] PASSED
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[es] PASSED
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[pa] PASSED ✅
test_voice_all_languages.py::TestVoiceModelsAllLanguages::test_tts_voice_mapping[zh] PASSED

============================== 36 passed in 2.5s ===============================
```

### Interpreting Results

- **PASSED:** Feature working correctly
- **FAILED:** Issue detected, check error message
- **SKIPPED:** Test requires additional setup (e.g., API key)
- **WARNING:** Non-critical issue, may still work

---

## 🔐 Security Notes

### API Keys
- Never commit API keys to git
- Use environment variables
- Rotate keys regularly

### Privacy
- Browser TTS/STT may send data to cloud
- OpenAI TTS sends text to OpenAI servers
- Check privacy policies

---

## 📚 Additional Resources

### Documentation
- [Voice Models Documentation](../VOICE_MODELS_DOCUMENTATION.md)
- [OpenAI TTS Guide](https://platform.openai.com/docs/guides/text-to-speech)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### Related Files
- `backend/app/main.py` - TTS/STT endpoints
- `frontend/src/components/VoiceChat.jsx` - Voice chat component
- `frontend/src/components/ChatInterface.jsx` - Voice preferences

---

## 🤝 Contributing

### Adding New Language Tests

1. Update `SUPPORTED_LANGUAGES` in `test_voice_all_languages.py`
2. Add language to `languages` object in `test_voice_browser.html`
3. Update backend `voice_map` in `backend/app/main.py`
4. Update frontend `langMap` in `VoiceChat.jsx`
5. Run tests to verify

### Reporting Issues

Include:
- Language code (e.g., `pa`)
- Browser and version
- Test output
- Error messages
- Diagnostic report

---

## ✅ Checklist

Before deploying:

- [ ] All automated tests pass
- [ ] Browser tests work for all languages
- [ ] Punjabi voice specifically tested
- [ ] OpenAI API key configured
- [ ] Documentation updated
- [ ] No sensitive data in code

---

**Last Updated:** January 9, 2026
**Test Coverage:** 6 languages, 36+ test cases
**Status:** ✅ All tests passing
