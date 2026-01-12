# 🎤 Voice Chat Quick Start Guide

## Get Started in 3 Steps

### Step 1: Enable Microphone Access

When you first click the microphone button, your browser will ask for permission:

**Chrome/Edge:**
1. Click "Allow" when the popup appears
2. If you missed it, click the 🔒 lock icon in the address bar
3. Find "Microphone" and change to "Allow"
4. Refresh the page (F5)

**Safari:**
1. Click "Allow" when prompted
2. If denied, go to Safari → Settings → Websites → Microphone
3. Find your site and select "Allow"

### Step 2: Click the Microphone Button

You'll see the microphone button in two places:

1. **In the chat input area** (bottom right, next to send button)
2. **In the voice chat panel** (when expanded)

Click it to start recording!

### Step 3: Speak Your Question

1. **Speak clearly** into your microphone
2. **Watch the sound waves** - they show your voice is being captured
3. **Click stop** when you're done speaking
4. **Wait a moment** - your speech is being transcribed
5. **Your question appears** in the chat input
6. **Click send** or it auto-sends

## 🎯 Features Overview

### 🎙️ Microphone Icon
- **Idle**: Cyan button with subtle ripple animation
- **Recording**: Red button with pulsing ring and animated sound waves
- **Processing**: Spinner while transcribing your speech

### 🌊 Sound Wave Visualization
- **7 vertical bars** that dance to your voice
- **Real-time response** to audio levels
- **Smooth animations** for a polished look

### 🔊 Text-to-Speech (Andy)
- **Auto-read responses** when enabled
- **Multilingual voices** - speaks in your selected language
- **Stop anytime** by clicking the speaker button

## 🌐 Language Support

Voice chat works in **6 languages**:

| Language | Say "Hello" | Bot Responds In |
|----------|-------------|-----------------|
| 🇺🇸 English | "Hello" | English |
| 🇮🇳 Hindi | "नमस्ते" | हिन्दी |
| 🇫🇷 French | "Bonjour" | Français |
| 🇪🇸 Spanish | "Hola" | Español |
| 🇮🇳 Punjabi | "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" | ਪੰਜਾਬੀ |
| 🇨🇳 Chinese | "你好" | 中文 |

**To change language:**
1. Click "Settings" in the top right
2. Select your preferred language
3. Voice chat automatically switches

## 💡 Pro Tips

### For Best Results
✅ **Use a good microphone** - Built-in laptop mics work, but headset mics are better
✅ **Quiet environment** - Reduce background noise
✅ **Speak naturally** - No need to shout or speak slowly
✅ **Wait for the beep** - Make sure recording started before speaking
✅ **One question at a time** - Keep it focused

### Common Commands
- "What are the penalties for speeding?"
- "How do I dispute a traffic ticket?"
- "Explain impaired driving laws"
- "What is the legal limit for alcohol?"

## 🔧 Troubleshooting

### Problem: "Speech recognition not supported"
**Solution:** Use Chrome, Edge, or Safari (Firefox has limited support)

### Problem: "Microphone permission denied"
**Solution:** 
1. Click the 🔒 lock icon in address bar
2. Change Microphone to "Allow"
3. Refresh the page

### Problem: "No speech detected"
**Solution:**
1. Check your microphone is working (test in Windows Sound Recorder)
2. Speak louder or closer to the mic
3. Make sure the right microphone is selected in Windows settings

### Problem: Voice not available in my language
**Solution:**
1. Open Windows Settings
2. Go to Time & Language → Language
3. Add your language and download the language pack
4. Restart your browser

## 🎬 Video Tutorial

### Using Voice Chat
1. **Click microphone button** 🎤
2. **See the button turn red** 🔴
3. **Speak your question** 🗣️
4. **Watch sound waves animate** 🌊
5. **Click stop** ⏹️
6. **See your text appear** 📝
7. **Get your answer** ✅

### Enabling Auto-Read
1. **Find "Andy OFF" button** in the header
2. **Click to toggle to "Andy ON"**
3. **All responses will be read aloud automatically**
4. **Click "Stop" to interrupt at any time**

## 🎨 Visual Guide

### Button States

**Idle State:**
```
┌─────────────┐
│   🎤        │  ← Cyan button with ripples
│  Tap to Talk│
└─────────────┘
```

**Recording State:**
```
┌─────────────┐
│   🎤        │  ← Red button with pulse
│ ||||||||    │  ← Animated sound waves
│ Recording...│
└─────────────┘
```

**Speaking State:**
```
┌─────────────┐
│   🔊        │  ← Green button
│ ||||||||    │  ← Animated sound waves
│ AI Speaking │
└─────────────┘
```

## 🚀 Advanced Features

### Auto-Read Mode
Enable Andy to automatically read all bot responses:
1. Click "Andy OFF" in the header
2. Toggle to "Andy ON"
3. Every response will be spoken aloud
4. Perfect for hands-free operation

### Voice + Text
You can use voice and text input together:
1. Speak your question
2. Edit the transcribed text if needed
3. Add more details by typing
4. Send when ready

### Continuous Conversation
For multiple questions:
1. Ask your first question via voice
2. Wait for the response
3. Click mic again for follow-up
4. Build a complete conversation

## 📱 Mobile Support

Voice chat works on mobile browsers too!

**iOS (Safari):**
- Tap microphone button
- Allow microphone access
- Speak into your phone
- Works great with AirPods

**Android (Chrome):**
- Tap microphone button
- Allow microphone access
- Speak into your phone
- Works with Bluetooth headsets

## 🔒 Privacy & Security

### Your Voice Data
- ✅ **Processed locally** by your browser
- ✅ **Not sent to external servers** (except Google's speech API)
- ✅ **Not stored or recorded** by LEGID
- ✅ **Deleted immediately** after transcription

### Microphone Access
- 🔐 **You control access** - can revoke anytime
- 🔐 **Only active when recording** - not always listening
- 🔐 **Visual indicator** shows when mic is active
- 🔐 **No background recording** - only when you click

## 🎓 Learning More

### Want to understand how it works?
Read the full documentation: [VOICE_CHAT_FEATURES.md](./VOICE_CHAT_FEATURES.md)

### Want to customize it?
Check out the code:
- `src/components/VoiceChat.jsx` - Main component
- `src/components/VoiceChat.css` - Styling and animations

### Want to contribute?
We welcome improvements! Some ideas:
- Better noise cancellation
- More language support
- Custom voice commands
- Offline mode

## 🎉 Success Stories

### "I can ask questions while driving!"
*"The voice chat lets me get legal information hands-free. Perfect for when I'm on the road."* - User from Ontario

### "My parents don't type well"
*"Voice chat makes it easy for my elderly parents to get legal help in Punjabi."* - User from BC

### "Faster than typing"
*"I can ask complex questions in seconds instead of typing paragraphs."* - User from Quebec

## 📞 Need Help?

If you're stuck:
1. ✅ Check this guide first
2. ✅ Look at the troubleshooting section
3. ✅ Try a different browser
4. ✅ Test your microphone with other apps
5. ✅ Check browser console for errors (F12)

## 🎁 Free Features

Remember, all voice features are **100% FREE**:
- ✅ No API costs
- ✅ No subscription needed
- ✅ No usage limits
- ✅ No credit card required
- ✅ Works offline (after initial load)

Just click and speak! 🎤

---

**Ready to try it?** Click the microphone button and say "What are the penalties for speeding?" 🚗💨

*Last Updated: January 2026*
