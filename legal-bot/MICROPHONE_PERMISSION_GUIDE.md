# Microphone Permission Guide

## Issue: "Microphone access denied"

This happens when your browser hasn't been given permission to access the microphone.

## Quick Fix - Allow Microphone Access

### Option 1: Browser Address Bar (Fastest)

1. **Look for the 🔒 lock icon** in your browser's address bar (next to the URL)
2. **Click the lock icon**
3. Find **"Microphone"** in the permissions list
4. Change it to **"Allow"**
5. **Reload the page** (F5 or Ctrl+R)
6. Click the **🎙️ microphone button** again

---

### Option 2: Browser Settings

#### Google Chrome / Microsoft Edge:

1. Click the **⋮** menu (three dots) → **Settings**
2. Go to **Privacy and security** → **Site Settings**
3. Click **Microphone**
4. Under **"Allowed to use your microphone"**, click **Add**
5. Enter: `http://localhost:4201` (or your frontend URL)
6. Click **Add**
7. Reload the page
8. Try voice chat again

#### Mozilla Firefox:

1. Click the **🛡️ shield icon** in the address bar
2. Click **Permissions** → **Microphone**
3. Select **"Allow"**
4. Reload the page
5. Try voice chat again

#### Safari (Mac):

1. Go to **Safari** → **Settings** (or Preferences)
2. Click **Websites** tab
3. Click **Microphone** in the left sidebar
4. Find `localhost` in the list
5. Change to **"Allow"**
6. Reload the page
7. Try voice chat again

---

### Option 3: First-Time Permission Prompt

If you accidentally clicked "Block" when the browser first asked for microphone access:

1. **Clear the site's permissions**:
   - Chrome/Edge: Settings → Privacy and security → Site Settings → View permissions and data stored across sites → Search "localhost" → Clear permissions
   - Firefox: Click lock icon → Clear cookies and site data
   - Safari: Settings → Websites → Microphone → Remove localhost

2. **Reload the page** (F5)

3. **Click the microphone button** - browser will ask again

4. **Click "Allow"** this time

---

## Visual Guide

### What You'll See:

**Browser Permission Prompt (First Time):**
```
┌─────────────────────────────────────────┐
│ 🎤 localhost wants to use your          │
│    microphone                            │
│                                          │
│    [Block]  [Allow]                     │
└─────────────────────────────────────────┘
```
**Click "Allow"!**

**Lock Icon Method:**
```
Address Bar: 
🔒 http://localhost:4201
  ↓ Click here
  
Permissions:
  🎤 Microphone: [Blocked ▼]
                    ↓ Change to
                 [Allow ▼]
```

---

## Testing Microphone

After allowing access:

1. Click **🎙️ Voice Chat** button in input area
2. Voice chat panel opens above messages
3. Click **"Tap to Talk"** (blue button)
4. You should see:
   - Recording dot (pulsing red)
   - Audio levels moving
   - "Recording..." text

If you see this, **microphone is working!** ✅

---

## Troubleshooting

### Problem: Permission is "Allow" but still not working

**Solution 1**: Reload the page completely (Ctrl+Shift+R to hard refresh)

**Solution 2**: Close and reopen the browser

**Solution 3**: Check if another app is using the microphone (Zoom, Teams, Discord, etc.)

### Problem: No microphone detected

**Solution**: 
1. Check if microphone is plugged in (for external mics)
2. Windows: Settings → System → Sound → Input → Test your microphone
3. Mac: System Preferences → Sound → Input → Select your microphone

### Problem: Browser says "No microphone found"

**Solution**:
1. Plug in a microphone or headset
2. Or enable built-in laptop microphone in system settings
3. Restart browser after connecting microphone

---

## Security & Privacy

### Why does the app need microphone access?

- To convert your speech to text using OpenAI Whisper
- Only records when you click "Tap to Talk"
- Recording stops when you click again
- Audio is only sent to OpenAI for transcription
- Not stored or recorded anywhere

### Is it safe?

✅ **Yes, it's safe:**
- Microphone is ONLY active when you click "Tap to Talk"
- Visual indicator (red pulsing dot) shows when recording
- You control when to start and stop
- Audio is processed by OpenAI (secure, GDPR-compliant)
- No audio is saved or stored

### Can I use voice chat without allowing microphone?

❌ No, you need to allow microphone access to use voice chat.

✅ Alternative: Use the text input (type your questions) instead of voice.

---

## Still Having Issues?

### Check Browser Console for Errors:

1. Press **F12** to open Developer Tools
2. Click **Console** tab
3. Look for errors (red text)
4. Common errors:
   - "NotAllowedError" = Permission denied
   - "NotFoundError" = No microphone detected
   - "NotSupportedError" = Browser doesn't support audio recording

### Browser Compatibility:

✅ **Supported:**
- Chrome 60+ (recommended)
- Edge 79+ (recommended)
- Firefox 55+
- Safari 11+
- Opera 47+

❌ **Not Supported:**
- Internet Explorer (any version)
- Very old browser versions

---

## Quick Reference

| Browser | How to Allow Microphone |
|---------|-------------------------|
| Chrome | Lock icon → Microphone → Allow |
| Edge | Lock icon → Microphone → Allow |
| Firefox | Shield icon → Permissions → Microphone → Allow |
| Safari | Safari → Settings → Websites → Microphone → Allow |

**Remember to reload the page after changing permissions!**

---

## Summary

1. ✅ Click lock icon in address bar
2. ✅ Change Microphone to "Allow"
3. ✅ Reload page (F5)
4. ✅ Click 🎙️ microphone button
5. ✅ Click "Tap to Talk"
6. ✅ Speak your question
7. ✅ Bot transcribes and responds!

Now you can have voice conversations with the AI! 🎙️🤖
