import React, { useState, useRef, useEffect } from 'react';
import './VoiceChat.css';

const VoiceChat = ({ preferences, lawTypeSelection, onTranscript, onAutoReadToggle }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState('');
  const [autoReadEnabled, setAutoReadEnabled] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const autoStopTimeoutRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.log('Recognition already stopped');
        }
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      if (autoStopTimeoutRef.current) {
        clearTimeout(autoStopTimeoutRef.current);
      }
    };
  }, []);

  // Start voice recording (FREE - uses browser's speech recognition)
  const startRecording = async () => {
    try {
      setError('');
      setTranscript('');
      
      // Enable auto-read when user clicks "Tap to Talk"
      if (!autoReadEnabled) {
        setAutoReadEnabled(true);
        // Notify parent component to enable auto-read
        if (onAutoReadToggle) {
          onAutoReadToggle(true);
        }
        // Show notification
        console.log('🔊 Auto-read enabled - Bot will read all responses aloud');
      }
      
      // Check browser support
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        setError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
        return;
      }
      
      // Create a FRESH recognition instance each time
      const recognition = new SpeechRecognition();
      recognition.continuous = true;  // Keep listening for longer
      recognition.interimResults = true;  // Show interim results
      recognition.maxAlternatives = 1;
      
      // Set language based on preferences
      const langMap = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'fr': 'fr-FR',
        'es': 'es-ES',
        'pa': 'pa-IN',
        'zh': 'zh-CN'
      };
      recognition.lang = langMap[preferences?.language?.code || 'en'] || 'en-US';
      
      // Start recording timer
      setRecordingTime(0);
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // Auto-stop after 30 seconds
      autoStopTimeoutRef.current = setTimeout(() => {
        if (recognitionRef.current) {
          stopRecording();
        }
      }, 30000);
      
      // Handle results
      let finalTranscript = '';
      recognition.onresult = (event) => {
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }
        
        // Update display with interim or final transcript
        setTranscript(finalTranscript + interimTranscript);
      };
      
      // Handle speech end
      recognition.onspeechend = () => {
        // Wait a bit for final results
        setTimeout(() => {
          if (recognitionRef.current && finalTranscript.trim()) {
            stopRecording();
            
            // Send final transcript to parent
            if (onTranscript) {
              onTranscript(finalTranscript.trim());
            }
          }
        }, 500);
      };
      
      // Handle errors
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        setIsProcessing(false);
        
        // Clear timers
        if (recordingTimerRef.current) {
          clearInterval(recordingTimerRef.current);
        }
        if (autoStopTimeoutRef.current) {
          clearTimeout(autoStopTimeoutRef.current);
        }
        
        if (event.error === 'not-allowed') {
          setError('🎤 Microphone access denied. Please allow microphone in browser settings.');
        } else if (event.error === 'no-speech') {
          setError(`Call ended in ${recordingTime} sec`);
        } else if (event.error === 'aborted') {
          console.log('Recognition aborted, resetting...');
          setError(`Call ended in ${recordingTime} sec`);
        } else if (event.error === 'audio-capture') {
          setError('🎤 No microphone found. Please connect a microphone.');
        } else if (event.error === 'network') {
          setError('Network error. Please check your connection.');
        } else {
          setError(`Call ended in ${recordingTime} sec`);
        }
      };
      
      recognition.onend = () => {
        setIsRecording(false);
        setIsProcessing(false);
        
        // Clear timers
        if (recordingTimerRef.current) {
          clearInterval(recordingTimerRef.current);
        }
        if (autoStopTimeoutRef.current) {
          clearTimeout(autoStopTimeoutRef.current);
        }
        
        // Show call ended message if no transcript
        if (!finalTranscript.trim() && recordingTime > 0) {
          setError(`Call ended in ${recordingTime} sec`);
        }
      };
      
      // Store the new instance
      recognitionRef.current = recognition;
      
      // Setup audio visualization
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        source.connect(analyserRef.current);
        analyserRef.current.fftSize = 256;
        visualizeAudio();
      } catch (e) {
        console.warn('Audio visualization not available:', e);
      }
      
      // Start FREE speech recognition
      recognition.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Failed to start recording. Please check microphone permissions.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (recognitionRef.current) {
      try {
        if (isRecording) {
          recognitionRef.current.stop();
          setIsProcessing(true); // Show processing while waiting for result
        }
      } catch (e) {
        console.log('Recognition already stopped:', e);
        setIsRecording(false);
        setIsProcessing(false);
      }
      
      setAudioLevel(0);
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
      
      // Clear timers
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
      }
      if (autoStopTimeoutRef.current) {
        clearTimeout(autoStopTimeoutRef.current);
      }
    }
  };

  // Visualize audio levels
  const visualizeAudio = () => {
    if (!analyserRef.current) return;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateLevel = () => {
      if (!isRecording) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(Math.min(100, (average / 255) * 100));
      
      requestAnimationFrame(updateLevel);
    };
    
    updateLevel();
  };

  // Speak using FREE browser TTS (Web Speech Synthesis API - same as Andy)
  const speakText = (text) => {
    if (!('speechSynthesis' in window)) {
      console.error('Text-to-speech not supported');
      return;
    }
    
    setIsSpeaking(true);
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language
    const langMap = {
      'en': 'en-US',
      'hi': 'hi-IN',
      'fr': 'fr-FR',
      'es': 'es-ES',
      'pa': 'pa-IN',
      'zh': 'zh-CN'
    };
    utterance.lang = langMap[preferences?.language?.code || 'en'] || 'en-US';
    
    // Select best voice for language
    const voices = window.speechSynthesis.getVoices();
    const selectedLang = preferences?.language?.code || 'en';
    
    const voicePreferences = {
      'en': ['Microsoft Mark', 'Microsoft David', 'Google US English Male'],
      'hi': ['Google हिन्दी', 'Microsoft Hemant', 'Google Hindi'],
      'fr': ['Google français', 'Microsoft Paul', 'Google French'],
      'es': ['Google español', 'Microsoft Pablo', 'Google Spanish'],
      'pa': ['Google ਪੰਜਾਬੀ', 'Google Punjabi'],
      'zh': ['Google 普通话', 'Microsoft Kangkang', 'Google Chinese']
    };
    
    const preferredNames = voicePreferences[selectedLang] || voicePreferences['en'];
    let selectedVoice = null;
    
    // Try to find preferred voice
    for (const name of preferredNames) {
      selectedVoice = voices.find(v => v.name.includes(name));
      if (selectedVoice) {
        console.log('🔊 Using voice:', selectedVoice.name);
        break;
      }
    }
    
    // Fallback to language code match
    if (!selectedVoice) {
      selectedVoice = voices.find(v => v.lang.startsWith(selectedLang));
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }
    
    // Voice settings
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    utterance.onend = () => {
      setIsSpeaking(false);
    };
    
    utterance.onerror = () => {
      setIsSpeaking(false);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Toggle auto-read mode
  const toggleAutoRead = () => {
    const newState = !autoReadEnabled;
    setAutoReadEnabled(newState);
    
    // Notify parent component
    if (onAutoReadToggle) {
      onAutoReadToggle(newState);
    }
    
    // Stop speaking if disabling
    if (!newState && isSpeaking) {
      stopSpeaking();
    }
    
    console.log(newState ? '🔊 Auto-read enabled' : '🔇 Auto-read disabled');
  };

  // Expose speak function to parent
  useEffect(() => {
    window.voiceChatSpeak = speakText;
    return () => {
      delete window.voiceChatSpeak;
    };
  }, [preferences]);

  return (
    <div className="voice-chat-container">
      {error && (
        <div className="voice-error">
          {error}
        </div>
      )}
      
      <div className="voice-info">
        🎤 <strong>FREE Voice Chat</strong> - Listens for up to 30 seconds. No API costs!
        {autoReadEnabled && (
          <div className="auto-read-badge">
            🔊 Auto-read is ON - Bot will read all responses aloud
          </div>
        )}
      </div>
      
      {/* Auto-Read Toggle Button */}
      <div className="auto-read-controls">
        <button 
          className={`auto-read-toggle ${autoReadEnabled ? 'active' : ''}`}
          onClick={toggleAutoRead}
          title={autoReadEnabled ? 'Turn off auto-read' : 'Turn on auto-read'}
        >
          {autoReadEnabled ? '🔊 Auto-Read: ON' : '🔇 Auto-Read: OFF'}
        </button>
        <span className="auto-read-hint">
          {autoReadEnabled 
            ? 'Bot will read all responses aloud automatically' 
            : 'Click "Tap to Talk" to enable auto-read'}
        </span>
      </div>
      
      <div className="voice-controls">
        {!isRecording && !isProcessing && !isSpeaking && (
          <button 
            className="voice-btn voice-btn-start"
            onClick={startRecording}
            title="Start voice chat"
          >
            <div className="mic-icon-container">
              <svg className="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
              <div className="mic-ripple"></div>
              <div className="mic-ripple mic-ripple-delay"></div>
            </div>
            <span>Tap to Talk</span>
          </button>
        )}
        
        {isRecording && (
          <button 
            className="voice-btn voice-btn-stop"
            onClick={stopRecording}
            title="Stop recording"
          >
            <div className="recording-indicator">
              <div className="mic-icon-container active">
                <svg className="mic-icon recording" width="32" height="32" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
                <div className="pulse-ring" style={{ transform: `scale(${1 + audioLevel / 100})` }}></div>
              </div>
              <div className="sound-wave-container">
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 0.8)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 1.0)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 0.6)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 0.9)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 0.7)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 1.0)}%` }}></div>
                <div className="sound-wave-bar" style={{ height: `${Math.max(20, audioLevel * 0.5)}%` }}></div>
              </div>
            </div>
            <span>Recording... {recordingTime}s (Tap to stop)</span>
          </button>
        )}
        
        {isProcessing && (
          <div className="voice-status">
            <div className="spinner"></div>
            <span>Processing your voice...</span>
          </div>
        )}
        
        {isSpeaking && (
          <button 
            className="voice-btn voice-btn-speaking"
            onClick={stopSpeaking}
            title="Stop speaking"
          >
            <div className="speaking-indicator">
              <svg className="speaker-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path className="sound-wave-1" d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                <path className="sound-wave-2" d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              </svg>
              <div className="sound-wave-container speaking">
                <div className="sound-wave-bar"></div>
                <div className="sound-wave-bar"></div>
                <div className="sound-wave-bar"></div>
                <div className="sound-wave-bar"></div>
                <div className="sound-wave-bar"></div>
              </div>
            </div>
            <span>AI Speaking... (Tap to stop)</span>
          </button>
        )}
      </div>
      
      {isRecording && (
        <div className="voice-timer">
          ⏱️ Recording: {recordingTime}s / 30s
        </div>
      )}
      
      {transcript && (
        <div className="voice-transcript">
          <span className="transcript-label">You said:</span>
          <p className="transcript-text">{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceChat;
