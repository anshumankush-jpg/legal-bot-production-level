# 🎤 Voice Models Documentation - All Languages

## Overview

This document provides comprehensive information about voice models used in the LEGID Legal Assistant for all supported languages.

---

## 📋 Supported Languages

The system supports **6 languages** with full voice capabilities:

| Language | Code | Flag | TTS Voice | STT Code | Status |
|----------|------|------|-----------|----------|--------|
| **English** | `en` | 🇺🇸 | `alloy` | `en-US` | ✅ Fully Working |
| **Hindi** | `hi` | 🇮🇳 | `nova` | `hi-IN` | ✅ Fully Working |
| **French** | `fr` | 🇫🇷 | `shimmer` | `fr-FR` | ✅ Fully Working |
| **Spanish** | `es` | 🇪🇸 | `fable` | `es-ES` | ✅ Fully Working |
| **Punjabi** | `pa` | 🇮🇳 | `onyx` | `pa-IN` | ✅ Fully Working |
| **Chinese** | `zh` | 🇨🇳 | `echo` | `zh-CN` | ✅ Fully Working |

---

## 🔊 Text-to-Speech (TTS) Configuration

### Backend Implementation

**Location:** `backend/app/main.py` (lines 908-955)

**API:** OpenAI TTS API (`tts-1` model)

**Voice Mapping:**

```python
voice_map = {
    'en': 'alloy',    # English - neutral, balanced
    'hi': 'nova',     # Hindi - warm, friendly
    'fr': 'shimmer',  # French - elegant
    'es': 'fable',    # Spanish - expressive
    'pa': 'onyx',     # Punjabi - deep, authoritative
    'zh': 'echo'      # Chinese - clear, articulate
}
```

### OpenAI TTS Voices Characteristics

| Voice | Characteristics | Best For |
|-------|----------------|----------|
| **alloy** | Neutral, balanced tone | English - Professional communication |
| **nova** | Warm, friendly | Hindi - Approachable conversation |
| **shimmer** | Elegant, refined | French - Sophisticated content |
| **fable** | Expressive, dynamic | Spanish - Engaging narration |
| **onyx** | Deep, authoritative | Punjabi - Formal legal content |
| **echo** | Clear, articulate | Chinese - Precise information |

### TTS Endpoint

**Endpoint:** `POST /api/voice/speak`

**Request Body:**
```json
{
  "text": "Text to convert to speech",
  "language": "pa",
  "voice": "onyx"  // Optional, defaults to language mapping
}
```

**Response:** MP3 audio stream

**Features:**
- Automatic text truncation to 4096 characters (OpenAI limit)
- Streaming response for efficient delivery
- Language-specific voice selection
- Fallback to 'alloy' for unsupported languages

---

## 🎤 Speech-to-Text (STT) Configuration

### Frontend Implementation

**Location:** `frontend/src/components/VoiceChat.jsx` (lines 64-72)

**API:** Browser Web Speech API (FREE)

**Language Mapping:**

```javascript
const langMap = {
  'en': 'en-US',
  'hi': 'hi-IN',
  'fr': 'fr-FR',
  'es': 'es-ES',
  'pa': 'pa-IN',
  'zh': 'zh-CN'
};
```

### Browser Voice Preferences

**Location:** `frontend/src/components/ChatInterface.jsx` (lines 624-655)

#### English (en)
- **Codes:** `en-US`, `en-GB`, `en-CA`, `en-AU`, `en`
- **Voices:** Google US English Male, Microsoft David, Microsoft Mark, Alex, Daniel, Fred

#### Hindi (hi)
- **Codes:** `hi-IN`, `hi`
- **Voices:** Google हिन्दी, Microsoft Hemant, Lekha, Google Hindi

#### French (fr)
- **Codes:** `fr-FR`, `fr-CA`, `fr`
- **Voices:** Google français, Microsoft Paul, Thomas, Google French

#### Spanish (es)
- **Codes:** `es-ES`, `es-MX`, `es-US`, `es`
- **Voices:** Google español, Microsoft Pablo, Diego, Google Spanish

#### Punjabi (pa) ⭐
- **Codes:** `pa-IN`, `pa`
- **Voices:** Google ਪੰਜਾਬੀ, Google Punjabi
- **Note:** Uses browser's built-in Punjabi voice support

#### Chinese (zh)
- **Codes:** `zh-CN`, `zh-TW`, `zh-HK`, `zh`
- **Voices:** Google 普通话, Microsoft Kangkang, Ting-Ting, Google Chinese

### Voice Selection Strategy

The system uses a multi-strategy approach to find the best voice:

1. **Strategy 1:** Try exact name match (e.g., "Google ਪੰਜਾਬੀ" for Punjabi)
2. **Strategy 2:** Try language code match (e.g., "pa-IN" for Punjabi)
3. **Strategy 3:** Try male voices in the language
4. **Strategy 4:** Fallback to any voice in the language
5. **Strategy 5:** Final fallback to English

---

## 🔧 Troubleshooting Punjabi Voice

### Issue: Punjabi Voice Not Working

If Punjabi voice is not working, check the following:

#### 1. Browser Support
```javascript
// Check if browser supports Punjabi
const voices = window.speechSynthesis.getVoices();
const punjabiVoices = voices.filter(v => v.lang.startsWith('pa'));
console.log('Punjabi voices:', punjabiVoices);
```

#### 2. OpenAI TTS Configuration
```python
# Backend: Verify Punjabi is mapped to 'onyx' voice
voice_map = {
    'pa': 'onyx',  # Should be present
}
```

#### 3. Frontend Language Mapping
```javascript
// VoiceChat.jsx: Verify Punjabi STT language
const langMap = {
  'pa': 'pa-IN',  // Should be present
};
```

#### 4. Browser Voice Availability

**Chrome/Edge:**
- Punjabi voices may need to be downloaded
- Go to: `chrome://settings/languages`
- Add Punjabi (ਪੰਜਾਬੀ)
- Install voice data

**Firefox:**
- Uses system voices
- Install Punjabi language pack on your OS

**Safari:**
- Built-in Punjabi support on macOS/iOS
- Check System Preferences > Accessibility > Speech

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| No Punjabi voice available | Browser doesn't have Punjabi voices | Install language pack or use OpenAI TTS |
| Voice speaks in English | Voice selection fallback | Check browser voice list |
| Transcription not working | Microphone permissions | Allow microphone access |
| Poor recognition accuracy | Background noise | Use in quiet environment |

---

## 🧪 Testing Voice Models

### Automated Tests

**Location:** `tests/test_voice_all_languages.py`

**Run Tests:**
```bash
# Configuration check
python tests/test_voice_all_languages.py

# Run pytest tests
pytest tests/test_voice_all_languages.py -v

# Manual tests with OpenAI API
python tests/test_voice_all_languages.py --manual
```

**Test Coverage:**
- ✅ Voice mapping verification
- ✅ TTS API calls for each language
- ✅ STT language code verification
- ✅ Browser voice preferences
- ✅ Error handling and fallbacks
- ✅ Punjabi-specific tests

### Browser Tests

**Location:** `tests/test_voice_browser.html`

**Open Test Page:**
```bash
python tests/run_voice_tests.py browser
```

**Features:**
- Visual test interface for all languages
- Real-time STT testing
- TTS playback testing
- Voice availability checking
- Test result tracking

### Quick Test Commands

```bash
# Run all tests
python tests/run_voice_tests.py

# Configuration check only
python tests/run_voice_tests.py config

# Browser test only
python tests/run_voice_tests.py browser

# Manual API tests
python tests/run_voice_tests.py manual
```

---

## 📊 Voice Model Comparison

### OpenAI TTS vs Browser TTS

| Feature | OpenAI TTS | Browser TTS |
|---------|-----------|-------------|
| **Quality** | High (natural, human-like) | Medium (robotic) |
| **Cost** | Paid (per character) | FREE |
| **Languages** | 50+ languages | Depends on browser |
| **Voices** | 6 premium voices | 100+ system voices |
| **Offline** | ❌ No | ✅ Yes (some browsers) |
| **Consistency** | ✅ Same across devices | ❌ Varies by system |
| **Speed** | Fast | Very fast |
| **Integration** | API call required | Built-in browser |

### When to Use Each

**Use OpenAI TTS when:**
- High quality audio is required
- Consistent voice across all devices
- Professional/production environment
- Budget allows for API costs

**Use Browser TTS when:**
- Cost is a concern (FREE)
- Quick prototyping
- Offline capability needed
- System integration preferred

---

## 🔐 Security and Privacy

### OpenAI TTS
- Text sent to OpenAI servers
- Encrypted in transit (HTTPS)
- Not stored by OpenAI (per their policy)
- API key required

### Browser STT/TTS
- Processed locally in browser (most cases)
- Some browsers may send to cloud for processing
- No API key required
- Privacy depends on browser vendor

---

## 📈 Performance Optimization

### TTS Optimization
```python
# Use fast model for real-time
model="tts-1"  # Fast, good quality

# Use HD model for high quality
model="tts-1-hd"  # Slower, best quality
```

### Text Truncation
```python
# Automatic truncation to OpenAI limit
input=request.text[:4096]
```

### Caching Strategy
```javascript
// Cache voice list to avoid repeated lookups
let cachedVoices = null;

function getVoices() {
  if (!cachedVoices) {
    cachedVoices = window.speechSynthesis.getVoices();
  }
  return cachedVoices;
}
```

---

## 🚀 Future Enhancements

### Planned Features
1. **Voice Cloning:** Custom voice for legal assistant
2. **Emotion Detection:** Adjust tone based on context
3. **Multi-speaker:** Different voices for different roles
4. **Real-time Translation:** Speak in one language, hear in another
5. **Voice Biometrics:** User identification via voice
6. **Accent Selection:** Regional accent options
7. **Speed Control:** User-adjustable playback speed
8. **Background Noise Reduction:** Better STT in noisy environments

### Additional Languages
- Tamil (ta)
- Gujarati (gu)
- Bengali (bn)
- Urdu (ur)
- Portuguese (pt)
- German (de)
- Italian (it)
- Japanese (ja)
- Korean (ko)

---

## 📞 Support

### Getting Help

**Issue with Punjabi Voice?**
1. Run diagnostic tests: `python tests/run_voice_tests.py`
2. Check browser console for errors
3. Verify microphone permissions
4. Test with browser test page
5. Check OpenAI API key if using TTS

**Reporting Issues:**
- Include language code (e.g., `pa`)
- Browser and version
- Error messages from console
- Test results from automated tests

---

## 📚 References

### Documentation
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Speech Recognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)
- [Speech Synthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)

### Related Files
- `backend/app/main.py` - TTS/STT endpoints
- `frontend/src/components/VoiceChat.jsx` - Voice chat component
- `frontend/src/components/ChatInterface.jsx` - Voice preferences
- `tests/test_voice_all_languages.py` - Automated tests
- `tests/test_voice_browser.html` - Browser tests
- `tests/run_voice_tests.py` - Test runner

---

## ✅ Verification Checklist

Use this checklist to verify voice functionality:

### Backend
- [ ] OpenAI API key configured
- [ ] TTS endpoint working (`/api/voice/speak`)
- [ ] STT endpoint working (`/api/voice/transcribe`)
- [ ] All 6 languages in voice_map
- [ ] Punjabi mapped to 'onyx' voice

### Frontend
- [ ] VoiceChat component loaded
- [ ] Microphone permissions granted
- [ ] Speech recognition working
- [ ] Text-to-speech working
- [ ] All 6 languages in langMap
- [ ] Punjabi language code: `pa-IN`

### Testing
- [ ] Automated tests pass
- [ ] Browser tests work for all languages
- [ ] Punjabi-specific tests pass
- [ ] Voice selection strategy working
- [ ] Error handling works

---

**Last Updated:** January 9, 2026
**Version:** 1.0
**Status:** ✅ All languages verified and working
