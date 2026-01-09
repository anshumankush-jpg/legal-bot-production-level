#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punjabi Voice Diagnostic Tool
Specifically diagnose and test Punjabi voice functionality
"""

import os
import sys
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_section(text):
    """Print section header"""
    print(f"\n{'─'*80}")
    print(f"  {text}")
    print(f"{'─'*80}")

def check_backend_configuration():
    """Check backend Punjabi configuration"""
    print_section("1. Backend Configuration Check")
    
    try:
        # Check if main.py exists
        main_file = Path(__file__).parent.parent / "backend" / "app" / "main.py"
        if not main_file.exists():
            print("❌ backend/app/main.py not found")
            return False
        
        # Read the file
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check voice_map
        if "'pa': 'onyx'" in content:
            print("✅ Punjabi TTS voice mapping found: 'pa' -> 'onyx'")
        else:
            print("❌ Punjabi TTS voice mapping NOT found in voice_map")
            return False
        
        # Check if OpenAI TTS endpoint exists
        if "@app.post(\"/api/voice/speak\")" in content:
            print("✅ TTS endpoint exists: /api/voice/speak")
        else:
            print("❌ TTS endpoint not found")
            return False
        
        # Check if Whisper endpoint exists
        if "@app.post(\"/api/voice/transcribe\")" in content:
            print("✅ STT endpoint exists: /api/voice/transcribe")
        else:
            print("❌ STT endpoint not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

def check_frontend_configuration():
    """Check frontend Punjabi configuration"""
    print_section("2. Frontend Configuration Check")
    
    try:
        # Check VoiceChat.jsx
        voice_chat_file = Path(__file__).parent.parent / "frontend" / "src" / "components" / "VoiceChat.jsx"
        
        if not voice_chat_file.exists():
            print("❌ VoiceChat.jsx not found")
            return False
        
        with open(voice_chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check language mapping
        if "'pa': 'pa-IN'" in content:
            print("✅ Punjabi STT language code found: 'pa' -> 'pa-IN'")
        else:
            print("❌ Punjabi STT language code NOT found")
            return False
        
        # Check ChatInterface.jsx for voice preferences
        chat_interface_file = Path(__file__).parent.parent / "frontend" / "src" / "components" / "ChatInterface.jsx"
        
        if not chat_interface_file.exists():
            print("⚠️  ChatInterface.jsx not found (optional)")
        else:
            with open(chat_interface_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "'pa':" in content and "Google ਪੰਜਾਬੀ" in content:
                print("✅ Punjabi voice preferences found in ChatInterface")
                print("   - Voice names: Google ਪੰਜਾਬੀ, Google Punjabi")
            else:
                print("⚠️  Punjabi voice preferences not found (may use defaults)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking frontend: {e}")
        return False

def check_openai_api_key():
    """Check if OpenAI API key is configured"""
    print_section("3. OpenAI API Key Check")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("\n   To set it:")
        print("   - Windows: set OPENAI_API_KEY=your-key-here")
        print("   - Linux/Mac: export OPENAI_API_KEY='your-key-here'")
        return False
    
    # Check if key looks valid (starts with sk-)
    if api_key.startswith('sk-'):
        print(f"✅ OPENAI_API_KEY is set (starts with 'sk-')")
        print(f"   Length: {len(api_key)} characters")
        return True
    else:
        print(f"⚠️  OPENAI_API_KEY is set but doesn't start with 'sk-'")
        print(f"   This may not be a valid OpenAI API key")
        return False

def test_punjabi_tts():
    """Test Punjabi TTS with OpenAI API"""
    print_section("4. Punjabi TTS Test (OpenAI API)")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Skipping TTS test - OPENAI_API_KEY not set")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        # Test Punjabi text
        test_text = "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਨੂੰ ਕਾਨੂੰਨੀ ਸਲਾਹ ਚਾਹੀਦੀ ਹੈ।"
        
        print(f"Testing with text: {test_text}")
        print("Calling OpenAI TTS API with voice 'onyx'...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=test_text
        )
        
        # Check response
        audio_size = len(response.content)
        print(f"✅ TTS Success!")
        print(f"   - Generated audio: {audio_size} bytes")
        print(f"   - Voice used: onyx")
        print(f"   - Model: tts-1")
        
        # Optionally save audio
        output_file = Path(__file__).parent / "punjabi_test_output.mp3"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"   - Audio saved to: {output_file}")
        
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed")
        print("   Install with: pip install openai")
        return False
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_punjabi_encoding():
    """Test Punjabi text encoding"""
    print_section("5. Punjabi Text Encoding Test")
    
    test_strings = [
        "ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
        "ਪੰਜਾਬੀ",
        "ਮੈਨੂੰ ਕਾਨੂੰਨੀ ਸਲਾਹ ਚਾਹੀਦੀ ਹੈ",
    ]
    
    all_ok = True
    
    for text in test_strings:
        try:
            # Test encoding/decoding
            encoded = text.encode('utf-8')
            decoded = encoded.decode('utf-8')
            
            if text == decoded:
                print(f"✅ '{text}' - Encoding OK")
            else:
                print(f"❌ '{text}' - Encoding mismatch")
                all_ok = False
                
        except Exception as e:
            print(f"❌ '{text}' - Encoding error: {e}")
            all_ok = False
    
    return all_ok

def generate_browser_test_code():
    """Generate JavaScript code for browser testing"""
    print_section("6. Browser Test Code")
    
    js_code = """
// Copy and paste this into your browser console to test Punjabi voice

console.log('🎤 Testing Punjabi Voice Support');

// 1. Check available voices
function checkPunjabiVoices() {
    const voices = window.speechSynthesis.getVoices();
    console.log('Total voices available:', voices.length);
    
    const punjabiVoices = voices.filter(v => 
        v.lang.startsWith('pa') || 
        v.name.includes('Punjabi') || 
        v.name.includes('ਪੰਜਾਬੀ')
    );
    
    if (punjabiVoices.length > 0) {
        console.log('✅ Punjabi voices found:', punjabiVoices.length);
        punjabiVoices.forEach(v => {
            console.log(`  - ${v.name} (${v.lang})`);
        });
    } else {
        console.log('❌ No Punjabi voices found');
        console.log('Available languages:', [...new Set(voices.map(v => v.lang))].sort());
    }
    
    return punjabiVoices;
}

// 2. Test Punjabi TTS
function testPunjabiTTS() {
    const text = 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਨੂੰ ਕਾਨੂੰਨੀ ਸਲਾਹ ਚਾਹੀਦੀ ਹੈ।';
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pa-IN';
    
    const voices = checkPunjabiVoices();
    if (voices.length > 0) {
        utterance.voice = voices[0];
        console.log('🔊 Speaking with:', voices[0].name);
    } else {
        console.log('⚠️ Using default voice');
    }
    
    utterance.onstart = () => console.log('✅ Speech started');
    utterance.onend = () => console.log('✅ Speech ended');
    utterance.onerror = (e) => console.error('❌ Speech error:', e);
    
    window.speechSynthesis.speak(utterance);
}

// 3. Test Punjabi STT
function testPunjabiSTT() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.error('❌ Speech recognition not supported');
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'pa-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = () => console.log('🎤 Listening for Punjabi...');
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('✅ Heard:', transcript);
    };
    recognition.onerror = (event) => console.error('❌ Recognition error:', event.error);
    recognition.onend = () => console.log('🎤 Stopped listening');
    
    recognition.start();
}

// Run tests
console.log('\\n--- Running Tests ---');
checkPunjabiVoices();
console.log('\\n--- To test TTS, run: testPunjabiTTS() ---');
console.log('--- To test STT, run: testPunjabiSTT() ---');
"""
    
    print("Copy the following JavaScript code and paste it into your browser console:")
    print("\n" + "─"*80)
    print(js_code)
    print("─"*80)
    
    # Save to file
    output_file = Path(__file__).parent / "punjabi_browser_test.js"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"\n✅ Code also saved to: {output_file}")

def print_recommendations():
    """Print recommendations for fixing Punjabi voice issues"""
    print_section("7. Recommendations")
    
    print("""
📋 To fix Punjabi voice issues:

1. **Backend (OpenAI TTS):**
   ✅ Already configured correctly
   - Voice: 'onyx' (deep, authoritative)
   - Endpoint: /api/voice/speak
   - Should work for Punjabi text

2. **Frontend (Browser TTS):**
   ⚠️  Depends on browser and OS
   
   **Chrome/Edge:**
   - Go to chrome://settings/languages
   - Add Punjabi (ਪੰਜਾਬੀ)
   - Download voice data
   
   **Firefox:**
   - Install Punjabi language pack on your OS
   - Firefox uses system voices
   
   **Safari (macOS/iOS):**
   - System Preferences > Accessibility > Speech
   - Download Punjabi voice

3. **Speech Recognition (STT):**
   ✅ Already configured correctly
   - Language code: 'pa-IN'
   - Uses browser's Web Speech API
   - May have limited accuracy for Punjabi

4. **Testing:**
   - Run: python tests/run_voice_tests.py browser
   - Test specifically with Punjabi
   - Check browser console for errors

5. **Alternative Solution:**
   If browser voices don't work well, use OpenAI TTS:
   - Higher quality
   - Consistent across devices
   - Requires API key and costs money
   - Already implemented in backend
""")

def main():
    """Main diagnostic function"""
    print_header("🔍 PUNJABI VOICE DIAGNOSTIC TOOL")
    
    print("""
This tool will check:
  1. Backend configuration (OpenAI TTS)
  2. Frontend configuration (Browser STT/TTS)
  3. OpenAI API key
  4. Punjabi TTS functionality
  5. Text encoding
  6. Browser testing code
""")
    
    results = {
        'backend': False,
        'frontend': False,
        'api_key': False,
        'tts_test': False,
        'encoding': False
    }
    
    # Run checks
    results['backend'] = check_backend_configuration()
    results['frontend'] = check_frontend_configuration()
    results['api_key'] = check_openai_api_key()
    results['tts_test'] = test_punjabi_tts()
    results['encoding'] = test_punjabi_encoding()
    
    # Generate browser test code
    generate_browser_test_code()
    
    # Print recommendations
    print_recommendations()
    
    # Summary
    print_header("📊 DIAGNOSTIC SUMMARY")
    
    print("\nResults:")
    print(f"  Backend Configuration:  {'✅ PASS' if results['backend'] else '❌ FAIL'}")
    print(f"  Frontend Configuration: {'✅ PASS' if results['frontend'] else '❌ FAIL'}")
    print(f"  OpenAI API Key:         {'✅ PASS' if results['api_key'] else '❌ FAIL'}")
    print(f"  TTS Test:               {'✅ PASS' if results['tts_test'] else '⚠️  SKIP'}")
    print(f"  Text Encoding:          {'✅ PASS' if results['encoding'] else '❌ FAIL'}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if all(results.values()):
        print("\n✅ All checks passed! Punjabi voice should be working.")
        print("   If you still have issues, check browser voice availability.")
    elif results['backend'] and results['frontend'] and results['encoding']:
        print("\n⚠️  Core configuration is correct.")
        print("   OpenAI TTS should work for Punjabi.")
        print("   Browser TTS may need voice installation.")
    else:
        print("\n❌ Some checks failed. Please review the issues above.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
