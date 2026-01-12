
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
console.log('\n--- Running Tests ---');
checkPunjabiVoices();
console.log('\n--- To test TTS, run: testPunjabiTTS() ---');
console.log('--- To test STT, run: testPunjabiSTT() ---');
