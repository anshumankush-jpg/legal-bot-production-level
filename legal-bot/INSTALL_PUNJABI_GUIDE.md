# 📦 Install Punjabi Language Package - Complete Guide

**Step-by-step guide to install Punjabi voice on Windows**

---

## 🚀 Quick Install (Automated)

### Option 1: Run PowerShell Script (Easiest)

1. **Right-click on PowerShell** and select **"Run as Administrator"**

2. **Navigate to project folder:**
   ```powershell
   cd C:\Users\anshu\Downloads\production_level\legal-bot
   ```

3. **Run the installation script:**
   ```powershell
   .\install_punjabi_voice.ps1
   ```

4. **Follow the prompts:**
   - Press `y` to confirm installation
   - Wait for installation to complete
   - Restart computer when prompted

---

## 📋 Manual Installation (Step-by-Step)

### Method 1: Windows Settings (Recommended)

#### Step 1: Open Windows Settings
- Press `Win + I` on your keyboard
- OR Click Start → Settings ⚙️

#### Step 2: Go to Language Settings
- Click **"Time & Language"**
- Click **"Language"** (or "Language & region" on Windows 11)

#### Step 3: Add Punjabi Language
1. Click **"Add a language"** button
2. In the search box, type **"Punjabi"** or **"pa"**
3. You should see:
   - **Punjabi (India)** 🇮🇳
   - OR **ਪੰਜਾਬੀ (ਭਾਰਤ)** 🇮🇳

4. **Select it** and click **"Next"**

#### Step 4: Install Language Features
1. Check these boxes:
   - ✅ **Install language pack**
   - ✅ **Text-to-speech**
   - ✅ **Speech recognition** (optional)
   - ✅ **Handwriting** (optional)

2. Click **"Install"**

3. **Wait for download** (may take 5-15 minutes depending on internet speed)

#### Step 5: Download Speech Pack
1. After installation, click on **"Punjabi"** in the language list
2. Click **"Options"**
3. Under **"Speech"**, click **"Download"**
4. Wait for speech pack to download

#### Step 6: Restart
1. **Restart your computer** (important!)
2. After restart, **restart your browser**

---

### Method 2: PowerShell Command (Quick)

#### For Windows 10/11:

1. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

2. **Run this command:**
   ```powershell
   $list = Get-WinUserLanguageList
   $list.Add("pa-IN")
   Set-WinUserLanguageList $list -Force
   ```

3. **Install speech components:**
   ```powershell
   Add-WindowsCapability -Online -Name "Language.TextToSpeech~~~pa-IN~0.0.1.0"
   ```

4. **Restart your computer**

---

### Method 3: Control Panel (Windows 10)

1. **Open Control Panel**
2. Click **"Clock and Region"**
3. Click **"Language"**
4. Click **"Add a language"**
5. Select **"Punjabi (India)"**
6. Click **"Add"**
7. Click on **"Punjabi"** → **"Options"**
8. Download **"Speech"** pack
9. **Restart computer**

---

## ✅ Verify Installation

### Check in Windows Settings

1. Go to **Settings → Time & Language → Language**
2. You should see **"Punjabi (India)"** or **"ਪੰਜਾਬੀ (ਭਾਰਤ)"** in the list
3. Click on it → **Options**
4. Under **Speech**, it should say **"Speech pack installed"** ✅

### Check in PowerShell

```powershell
# Check installed languages
Get-WinUserLanguageList | Where-Object { $_.LanguageTag -eq "pa-IN" }

# Should return Punjabi language info
```

### Check in Browser

1. **Open the voice checker page:**
   ```
   legal-bot\tests\check_browser_voices.html
   ```

2. **Look for Punjabi voices:**
   - Should see "Google ਪੰਜਾਬੀ" or "Google Punjabi"
   - Should be highlighted in green ✅

3. **Test the voice:**
   - Click "Test" button next to Punjabi voice
   - Should hear Punjabi speech

---

## 🧪 Test Punjabi Voice

### Test Page 1: Voice Checker
```
Open: legal-bot\tests\check_browser_voices.html
```
- Shows all available voices
- Highlights Punjabi voices
- Test button for each voice

### Test Page 2: Voice Settings Demo
```
Open: legal-bot\tests\voice_settings_demo.html
```
- Select Punjabi language
- Choose male or female
- Test voice

### Test Page 3: Main Voice Test
```
Open: legal-bot\tests\test_voice_browser.html
```
- Comprehensive test for all languages
- Includes Punjabi

---

## 🐛 Troubleshooting

### Issue: "Punjabi not found in language list"

**Solution:**
1. Update Windows:
   - Settings → Update & Security → Windows Update
   - Install all updates
   - Restart and try again

2. Check Windows version:
   - Press `Win + R`, type `winver`, press Enter
   - Need Windows 10 version 1803 or later
   - Need Windows 11 version 21H2 or later

### Issue: "Speech pack download fails"

**Solution:**
1. Check internet connection
2. Disable VPN/Proxy temporarily
3. Try again later (Microsoft servers may be busy)
4. Use PowerShell method instead

### Issue: "Voice still not available in browser"

**Solution:**
1. **Restart computer** (not just browser!)
2. **Clear browser cache:**
   - Chrome: `Ctrl + Shift + Delete`
   - Select "All time"
   - Clear cache
3. **Restart browser completely:**
   - Close ALL browser windows
   - Open browser again
4. **Check browser console:**
   - Press `F12`
   - Go to Console tab
   - Run: `speechSynthesis.getVoices()`
   - Look for Punjabi voices

### Issue: "Installation stuck or frozen"

**Solution:**
1. Cancel installation
2. Restart computer
3. Try PowerShell method instead
4. Or use manual Windows Settings method

### Issue: "Not enough disk space"

**Solution:**
- Punjabi language pack needs ~100-200 MB
- Free up disk space
- Try again

---

## 📊 What Gets Installed

### Language Pack Components:

| Component | Size | Purpose |
|-----------|------|---------|
| **Language Pack** | ~50 MB | Basic language support |
| **Text-to-Speech** | ~50 MB | Voice synthesis |
| **Speech Recognition** | ~100 MB | Voice input (optional) |
| **Fonts** | ~10 MB | Gurmukhi script display |

**Total:** ~100-200 MB (depending on options selected)

---

## 🎯 After Installation

### 1. Restart Everything
```
1. Restart computer ✅
2. Restart browser ✅
3. Clear browser cache ✅
```

### 2. Verify Installation
```
1. Check Windows Settings ✅
2. Check browser voices ✅
3. Test voice in demo page ✅
```

### 3. Test in Application
```
1. Open your application
2. Select Punjabi language
3. Use voice features
4. Verify it works
```

---

## 🌐 Browser-Specific Notes

### Chrome/Edge (Chromium)
- ✅ Best support for Punjabi
- Uses Windows speech engine
- Voices available immediately after restart

### Firefox
- ✅ Good support
- Uses system voices
- May need to enable in `about:config`

### Safari (macOS)
- ❌ Punjabi not available on macOS
- Use OpenAI TTS instead

---

## 🔄 Alternative: OpenAI TTS

If you can't install Punjabi language pack, use OpenAI TTS:

### Setup:

1. **Get OpenAI API Key:**
   - Go to https://platform.openai.com
   - Create account
   - Get API key

2. **Set API Key:**
   ```powershell
   $env:OPENAI_API_KEY='your-api-key-here'
   ```

3. **Test:**
   ```bash
   python legal-bot/tests/test_punjabi_openai.py
   ```

### Advantages:
- ✅ High quality voice
- ✅ Works on any OS
- ✅ Consistent across devices
- ✅ No installation needed

### Disadvantages:
- ❌ Costs money (~$0.015 per 1000 characters)
- ❌ Requires internet
- ❌ Slight latency (~1-2 seconds)

---

## 📞 Need Help?

### Check These First:
1. ✅ Windows is updated
2. ✅ Computer restarted after installation
3. ✅ Browser restarted
4. ✅ Cache cleared

### Run Diagnostics:
```bash
# Check Punjabi configuration
python legal-bot/tests/diagnose_punjabi_voice.py

# Test with OpenAI (if API key set)
python legal-bot/tests/test_punjabi_openai.py
```

### Still Not Working?
1. Try OpenAI TTS as fallback
2. Check browser console for errors
3. Verify Windows version compatibility
4. Try different browser

---

## ✅ Installation Checklist

Use this checklist to track your progress:

### Pre-Installation
- [ ] Windows 10/11 installed
- [ ] Administrator access
- [ ] Internet connection
- [ ] ~200 MB free disk space

### Installation
- [ ] Language pack downloaded
- [ ] Speech pack downloaded
- [ ] Installation completed
- [ ] No errors shown

### Post-Installation
- [ ] Computer restarted
- [ ] Browser restarted
- [ ] Cache cleared
- [ ] Punjabi visible in language list

### Verification
- [ ] Punjabi in Windows Settings
- [ ] Speech pack installed
- [ ] Voice available in browser
- [ ] Test voice works
- [ ] Application uses Punjabi voice

---

## 🎉 Success!

Once installed, you should see:

### In Windows Settings:
```
✅ Punjabi (India) - ਪੰਜਾਬੀ (ਭਾਰਤ)
   Speech: Installed
   Text-to-speech: Available
```

### In Browser:
```
✅ Google ਪੰਜਾਬੀ (pa-IN)
✅ Google Punjabi (pa-IN)
```

### In Application:
```
✅ Punjabi voice selectable
✅ Voice test works
✅ Bot speaks in Punjabi
```

---

## 📚 Additional Resources

### Microsoft Documentation:
- [Add Language Packs](https://support.microsoft.com/en-us/windows/language-packs-for-windows-a5094319-a92d-18de-5b53-1cfc697cfca8)
- [Text-to-Speech](https://support.microsoft.com/en-us/windows/use-text-to-speech-in-windows-10-93e0c7c6-2e2e-4e1e-b3d0-c5e5c3e0e0e0)

### Browser Documentation:
- [Chrome Web Speech API](https://developer.chrome.com/blog/voice-driven-web-apps-introduction-to-the-web-speech-api/)
- [MDN Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### Project Documentation:
- `VOICE_MODELS_DOCUMENTATION.md` - Technical details
- `PUNJABI_VOICE_FIX.md` - Troubleshooting
- `ADVANCED_VOICE_SYSTEM.md` - Complete voice system

---

**Last Updated:** January 9, 2026  
**Status:** ✅ Complete Installation Guide  
**Support:** Run `diagnose_punjabi_voice.py` for diagnostics
