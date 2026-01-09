# ⚡ Quick Install Punjabi Voice - 3 Methods

**Choose the easiest method for you:**

---

## 🚀 Method 1: Double-Click Install (EASIEST)

### Steps:
1. **Double-click** `INSTALL_PUNJABI.bat` in this folder
2. Click **"Yes"** when asked for Administrator permission
3. Follow the prompts in PowerShell window
4. **Restart computer** when done

**Time:** 5-10 minutes + restart

---

## ⚡ Method 2: PowerShell Script (FAST)

### Steps:
1. **Right-click PowerShell** → **"Run as Administrator"**
2. **Navigate to folder:**
   ```powershell
   cd C:\Users\anshu\Downloads\production_level\legal-bot
   ```
3. **Run script:**
   ```powershell
   .\install_punjabi_voice.ps1
   ```
4. **Follow prompts** and restart

**Time:** 5-10 minutes + restart

---

## 🖱️ Method 3: Windows Settings (MANUAL)

### Steps:
1. Press `Win + I` (open Settings)
2. Go to **Time & Language** → **Language**
3. Click **"Add a language"**
4. Search **"Punjabi"** or **"pa"**
5. Select **"Punjabi (India)"** 🇮🇳
6. Click **"Install"**
7. After install, click **Punjabi** → **Options**
8. Under **Speech**, click **"Download"**
9. **Restart computer**

**Time:** 10-15 minutes + restart

---

## ✅ After Installation

### 1. Verify Installation
```powershell
# In PowerShell, run:
Get-WinUserLanguageList | Where-Object { $_.LanguageTag -eq "pa-IN" }
```

Should show Punjabi language info ✅

### 2. Test in Browser
1. Open: `tests\check_browser_voices.html`
2. Look for **"Google ਪੰਜਾਬੀ"** or **"Google Punjabi"**
3. Should be highlighted in green ✅
4. Click **"Test"** button to hear voice

### 3. Test in Application
1. Open: `tests\voice_settings_demo.html`
2. Click on **Punjabi** 🇮🇳
3. Select **Male** or **Female**
4. Click **"Test Selected Voice"**
5. Should hear Punjabi voice ✅

---

## 🐛 Troubleshooting

### Problem: "Access Denied" or "Permission Error"
**Solution:** Run PowerShell as Administrator

### Problem: "Script not found"
**Solution:** Make sure you're in the `legal-bot` folder

### Problem: "Voice still not available"
**Solution:** 
1. Restart computer (important!)
2. Restart browser
3. Clear browser cache

### Problem: "Download fails"
**Solution:** 
1. Check internet connection
2. Try again later
3. Use manual Windows Settings method

---

## 📊 What You'll Get

After installation:
- ✅ Punjabi language pack (~50 MB)
- ✅ Punjabi text-to-speech (~50 MB)
- ✅ Google ਪੰਜਾਬੀ voice (Male)
- ✅ Google Punjabi voice (Male/Female)
- ✅ Gurmukhi script support

**Total Size:** ~100-150 MB

---

## 🎯 Quick Commands

### Check if installed:
```powershell
Get-WinUserLanguageList | Where-Object { $_.LanguageTag -eq "pa-IN" }
```

### Install manually:
```powershell
$list = Get-WinUserLanguageList
$list.Add("pa-IN")
Set-WinUserLanguageList $list -Force
```

### Test voice:
```bash
# Open in browser:
tests\check_browser_voices.html
```

---

## ⏱️ Time Estimates

| Method | Time | Difficulty |
|--------|------|------------|
| **Batch File** | 5-10 min | ⭐ Easy |
| **PowerShell** | 5-10 min | ⭐⭐ Medium |
| **Windows Settings** | 10-15 min | ⭐ Easy |

**Plus:** Computer restart (~2-5 minutes)

---

## 🎉 Success Indicators

### You'll know it worked when:
1. ✅ Punjabi appears in Windows language list
2. ✅ "Speech pack installed" shows in language options
3. ✅ Browser shows "Google ਪੰਜਾਬੀ" voice
4. ✅ Test voice speaks in Punjabi
5. ✅ Application can use Punjabi voice

---

## 📞 Need Help?

### Run Diagnostics:
```bash
python tests\diagnose_punjabi_voice.py
```

### Check Full Guide:
- Read: `INSTALL_PUNJABI_GUIDE.md`
- Complete troubleshooting steps
- Alternative methods

### Still Not Working?
- Use OpenAI TTS (high quality, costs money)
- See: `test_punjabi_openai.py`

---

## 🚀 Ready to Install?

**Choose your method above and get started!**

**Estimated Total Time:** 10-20 minutes (including restart)

---

**Files:**
- `INSTALL_PUNJABI.bat` - Double-click to install
- `install_punjabi_voice.ps1` - PowerShell script
- `INSTALL_PUNJABI_GUIDE.md` - Complete guide
- `tests\check_browser_voices.html` - Test voices

**Status:** ✅ Ready to install
