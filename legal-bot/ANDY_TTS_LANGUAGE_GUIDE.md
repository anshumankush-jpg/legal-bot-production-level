# Andy TTS Multi-Language Support Guide

## ✅ Andy Already Speaks in Selected Language!

Andy TTS is **fully configured** to speak in the language you select. Here's how it works:

## Supported Languages

| Language | Code | Voices Available |
|----------|------|------------------|
| **English** | en | Google US English Male, Microsoft David, Microsoft Mark, Alex, Daniel, Fred |
| **Hindi (हिन्दी)** | hi | Google हिन्दी, Microsoft Hemant, Lekha, Google Hindi |
| **French (Français)** | fr | Google français, Microsoft Paul, Thomas, Google French |
| **Spanish (Español)** | es | Google español, Microsoft Pablo, Diego, Google Spanish |
| **Punjabi (ਪੰਜਾਬੀ)** | pa | Google ਪੰਜਾਬੀ, Google Punjabi |
| **Chinese (中文)** | zh | Google 普通话, Microsoft Kangkang, Ting-Ting, Google Chinese |

## How Andy Selects Voice (Automatic Process)

### Voice Selection Strategy:

1. **Strategy 1**: Try exact name match (e.g., "Google हिन्दी" for Hindi)
2. **Strategy 2**: Try language code match (e.g., "hi-IN" for Hindi)
3. **Strategy 3**: Try male voices in the language
4. **Strategy 4**: Fallback to any voice in the language
5. **Strategy 5**: Final fallback to English

### Example for Hindi:
```
User selects Hindi
    ↓
Andy looks for: "Google हिन्दी"
    ↓
If not found → looks for "Microsoft Hemant"
    ↓
If not found → looks for any "hi-IN" voice
    ↓
If not found → shows warning "Hindi voice not found"
    ↓
Fallback to English voice
```

## How to Test Andy in Hindi

### Step 1: Change Language to Hindi
1. Click **"Language: English"** badge (top left)
2. Select **"Hindi 🇮🇳"**
3. Select Canada → Ontario
4. Select any law type (e.g., Health Law)

### Step 2: Toggle Andy ON
1. Look for the **"Andy ON"** button in the chat header
2. Click it to enable auto-read (Andy will read all responses automatically)

### Step 3: Ask a Question
Type any question in English or Hindi:
```
"मेडिकल नेगलिजेंस क्या है?"
```

### Step 4: Listen to Andy Speak in Hindi
- Andy will automatically read the response in Hindi
- You'll see: `🎙️ Andy speaking in Hindi (Google हिन्दी)`
- The speaking indicator shows: `Andy speaking Hindi...`

## Visual Indicators When Andy Speaks

### 1. **System Message**
```
INFO: 🎙️ Andy speaking in Hindi (Google हिन्दी)
```

### 2. **Speaking Indicator**
```
🔊 Andy speaking Hindi...
[animated pulse]
```

### 3. **Console Log** (for debugging)
```
🎙️ Andy looking for Hindi voice from 50 available voices
✅ Found by name: Google हिन्दी
🎙️ Andy speaking in: Google हिन्दी (hi-IN)
```

## Installing Language Voices (If Not Available)

### Windows 10/11:
1. Go to **Settings** (Win + I)
2. Click **Time & Language**
3. Click **Language**
4. Click **Add a language**
5. Search for **Hindi (India)** or your language
6. Click **Next** → **Install**
7. Wait for download (includes voice pack)
8. Restart browser

### macOS:
1. Go to **System Preferences**
2. Click **Accessibility**
3. Click **Spoken Content**
4. Click **System Voice** → **Customize**
5. Check **Hindi** or your language
6. Click **OK** → Download
7. Restart browser

### Chrome/Edge:
- Uses Windows/Mac system voices
- Install language pack from OS (above)

### Firefox:
- Uses system voices
- Install from OS settings

## Testing Each Language

### English (Default)
```
Click speaker icon → "Welcome to PLAZA-AI Legal Assistant"
Voice: Google US English Male or Microsoft David
```

### Hindi
```
Select Hindi → Click speaker → "PLAZA-AI कानूनी सहायक में आपका स्वागत है"
Voice: Google हिन्दी or Microsoft Hemant
```

### French
```
Select French → Click speaker → "Bienvenue dans l'assistant juridique PLAZA-AI"
Voice: Google français or Microsoft Paul
```

### Spanish
```
Select Spanish → Click speaker → "¡Bienvenido al asistente legal PLAZA-AI!"
Voice: Google español or Microsoft Pablo
```

### Punjabi
```
Select Punjabi → Click speaker → "PLAZA-AI ਕਾਨੂੰਨੀ ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ"
Voice: Google ਪੰਜਾਬੀ
```

### Chinese
```
Select Chinese → Click speaker → "欢迎使用 PLAZA-AI 法律助手"
Voice: Google 普通话 or Microsoft Kangkang
```

## Troubleshooting

### Problem: Andy speaks in English even after selecting Hindi

**Solution 1**: Check if Hindi voice is installed
```
1. Open browser console (F12)
2. Look for message: "⚠️ Hindi voice not found"
3. Install Hindi language pack (see above)
4. Restart browser
```

**Solution 2**: Verify language selection
```
1. Check badge shows "Language: Hindi"
2. If not, click badge and reselect Hindi
3. Reload the page
```

**Solution 3**: Test available voices
```
1. Open browser console (F12)
2. Type: speechSynthesis.getVoices()
3. Look for Hindi voices in the list
4. If none found → install language pack
```

### Problem: No sound at all

**Solution**:
```
1. Check system volume (not muted)
2. Check browser permissions (allow audio)
3. Try clicking Stop button then Andy button again
4. Restart browser
```

### Problem: Voice quality is poor

**Solution**:
```
1. Install official language pack (not browser extension)
2. Prefer "Google" voices over "Microsoft" voices
3. Check speech rate in code (currently 0.95)
```

## Advanced: Manual Voice Testing

Open browser console and run:

```javascript
// Get all available voices
const voices = speechSynthesis.getVoices();
console.log('Available voices:', voices);

// Filter Hindi voices
const hindiVoices = voices.filter(v => v.lang.startsWith('hi'));
console.log('Hindi voices:', hindiVoices);

// Test speaking in Hindi
const utterance = new SpeechSynthesisUtterance('नमस्ते, मैं Andy हूं');
utterance.voice = hindiVoices[0];
utterance.lang = 'hi-IN';
speechSynthesis.speak(utterance);
```

## Features Enabled

✅ **Auto-detect selected language**
✅ **Automatic voice selection** (4 fallback strategies)
✅ **Real-time voice switching** (change language mid-session)
✅ **Voice availability check** (warns if not installed)
✅ **Multi-language support** (6 languages)
✅ **Natural speech rate** (0.95x for clarity)
✅ **Console logging** (for debugging)
✅ **User notifications** (which voice is being used)

## Current Implementation Status

| Feature | Status |
|---------|--------|
| Language detection from preferences | ✅ Working |
| Voice preferences for 6 languages | ✅ Configured |
| 4-strategy voice selection | ✅ Implemented |
| Console logging for debugging | ✅ Active |
| User notification on voice selection | ✅ Added |
| Warning if voice not available | ✅ Added |
| Fallback to English | ✅ Working |
| Auto-read in selected language | ✅ Working |

## Expected User Experience

### When Hindi voice IS installed:
1. Select Hindi
2. Click Andy ON or speaker icon
3. See: `🎙️ Andy speaking in Hindi (Google हिन्दी)`
4. Hear response in perfect Hindi voice

### When Hindi voice is NOT installed:
1. Select Hindi
2. Click Andy ON or speaker icon
3. See: `⚠️ Hindi voice not found. Install language pack from Windows Settings → Time & Language → Language. Using English voice as fallback.`
4. Hear response in English voice (temporary fallback)
5. Install Hindi language pack
6. Restart browser
7. Now Andy speaks in Hindi!

## Recommendation

**For best experience with Hindi:**
1. Install **Hindi (India)** language pack from Windows Settings
2. Restart browser after installation
3. Select Hindi in PLAZA-AI
4. Enable Andy auto-read
5. Enjoy legal assistance in Hindi!

## Files Involved

- `frontend/src/components/ChatInterface.jsx` - Andy TTS implementation
  - `getLanguageCode()` - Gets selected language
  - `handleReadAloud()` - Initiates speech
  - `setupAndyVoice()` - Selects appropriate voice (144 lines of voice selection logic!)

## Summary

✅ **Andy TTS is FULLY functional for all 6 languages**
✅ **Voice selection is automatic based on user's language preference**
✅ **Fallback mechanisms ensure it always works**
✅ **User gets notified which voice is being used**
⚠️ **Users need to install language packs for non-English languages**

**Test it now!** Select Hindi and click the speaker icon! 🎙️🇮🇳
