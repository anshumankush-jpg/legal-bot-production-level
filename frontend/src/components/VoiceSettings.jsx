import React, { useState, useEffect } from 'react';
import './VoiceSettings.css';

const VoiceSettings = ({ preferences, onVoiceChange, onTestVoice }) => {
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState(preferences?.language?.code || 'en');
  const [selectedGender, setSelectedGender] = useState('male');
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [isTesting, setIsTesting] = useState(false);

  // Language configuration with voice options
  const languageConfig = {
    en: {
      name: 'English',
      flag: '🇺🇸',
      testText: 'Hello! This is a test of the English voice. How does it sound?',
      voices: {
        male: [
          { name: 'Microsoft Mark', provider: 'Microsoft', quality: 'High' },
          { name: 'Microsoft David', provider: 'Microsoft', quality: 'High' },
          { name: 'Google US English Male', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Microsoft Zira', provider: 'Microsoft', quality: 'High' },
          { name: 'Google US English Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    },
    hi: {
      name: 'Hindi',
      flag: '🇮🇳',
      testText: 'नमस्ते! यह हिंदी आवाज का परीक्षण है। यह कैसा लगता है?',
      voices: {
        male: [
          { name: 'Microsoft Hemant', provider: 'Microsoft', quality: 'High' },
          { name: 'Google हिन्दी', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Microsoft Lekha', provider: 'Microsoft', quality: 'High' },
          { name: 'Google Hindi Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    },
    pa: {
      name: 'Punjabi',
      flag: '🇮🇳',
      testText: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਇਹ ਪੰਜਾਬੀ ਆਵਾਜ਼ ਦਾ ਟੈਸਟ ਹੈ। ਇਹ ਕਿਵੇਂ ਲੱਗਦਾ ਹੈ?',
      voices: {
        male: [
          { name: 'Google ਪੰਜਾਬੀ', provider: 'Google', quality: 'Medium' },
          { name: 'Google Punjabi Male', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Google Punjabi Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    },
    fr: {
      name: 'French',
      flag: '🇫🇷',
      testText: 'Bonjour! Ceci est un test de la voix française. Comment ça sonne?',
      voices: {
        male: [
          { name: 'Microsoft Paul', provider: 'Microsoft', quality: 'High' },
          { name: 'Google français', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Microsoft Hortense', provider: 'Microsoft', quality: 'High' },
          { name: 'Google French Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    },
    es: {
      name: 'Spanish',
      flag: '🇪🇸',
      testText: '¡Hola! Esta es una prueba de la voz en español. ¿Cómo suena?',
      voices: {
        male: [
          { name: 'Microsoft Pablo', provider: 'Microsoft', quality: 'High' },
          { name: 'Google español', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Microsoft Helena', provider: 'Microsoft', quality: 'High' },
          { name: 'Google Spanish Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    },
    zh: {
      name: 'Chinese',
      flag: '🇨🇳',
      testText: '你好！这是中文语音测试。听起来怎么样？',
      voices: {
        male: [
          { name: 'Microsoft Kangkang', provider: 'Microsoft', quality: 'High' },
          { name: 'Google 普通话', provider: 'Google', quality: 'Medium' }
        ],
        female: [
          { name: 'Microsoft Yaoyao', provider: 'Microsoft', quality: 'High' },
          { name: 'Google Chinese Female', provider: 'Google', quality: 'Medium' }
        ]
      }
    }
  };

  // Load available voices from browser
  useEffect(() => {
    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      setAvailableVoices(voices);
      
      // Auto-select best voice for current language
      if (voices.length > 0) {
        selectBestVoice(selectedLanguage, selectedGender, voices);
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [selectedLanguage, selectedGender]);

  // Select best available voice
  const selectBestVoice = (lang, gender, voices) => {
    const config = languageConfig[lang];
    if (!config) return;

    const preferredVoices = config.voices[gender] || config.voices.male;
    
    for (const voiceOption of preferredVoices) {
      const found = voices.find(v => v.name.includes(voiceOption.name));
      if (found) {
        setSelectedVoice(found);
        if (onVoiceChange) {
          onVoiceChange(found, lang, gender);
        }
        return;
      }
    }

    // Fallback to any voice in the language
    const fallback = voices.find(v => v.lang.startsWith(lang));
    if (fallback) {
      setSelectedVoice(fallback);
      if (onVoiceChange) {
        onVoiceChange(fallback, lang, gender);
      }
    }
  };

  // Handle language change
  const handleLanguageChange = (lang) => {
    setSelectedLanguage(lang);
    selectBestVoice(lang, selectedGender, availableVoices);
  };

  // Handle gender change
  const handleGenderChange = (gender) => {
    setSelectedGender(gender);
    selectBestVoice(selectedLanguage, gender, availableVoices);
  };

  // Test voice
  const handleTestVoice = () => {
    if (!selectedVoice) {
      alert('No voice selected. Please select a language and gender.');
      return;
    }

    setIsTesting(true);

    const config = languageConfig[selectedLanguage];
    const text = config?.testText || 'This is a test.';

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.lang = selectedVoice.lang;
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      console.log('🔊 Testing voice:', selectedVoice.name);
    };

    utterance.onend = () => {
      setIsTesting(false);
      console.log('✅ Voice test complete');
    };

    utterance.onerror = (e) => {
      setIsTesting(false);
      console.error('❌ Voice test error:', e);
      alert(`Voice test failed: ${e.error}`);
    };

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);

    if (onTestVoice) {
      onTestVoice(selectedVoice, text);
    }
  };

  // Check if voice is available
  const isVoiceAvailable = (voiceName) => {
    return availableVoices.some(v => v.name.includes(voiceName));
  };

  // Get available voices for current selection
  const getAvailableVoicesForSelection = () => {
    const config = languageConfig[selectedLanguage];
    if (!config) return [];

    const genderVoices = config.voices[selectedGender] || [];
    return genderVoices.map(voice => ({
      ...voice,
      available: isVoiceAvailable(voice.name)
    }));
  };

  return (
    <div className="voice-settings">
      <div className="voice-settings-header">
        <h2>🎤 Voice Settings</h2>
        <p>Customize your voice experience</p>
      </div>

      {/* Language Selection */}
      <div className="setting-section">
        <label className="setting-label">
          <span className="label-icon">🌐</span>
          Select Language
        </label>
        <div className="language-grid">
          {Object.entries(languageConfig).map(([code, config]) => (
            <button
              key={code}
              className={`language-option ${selectedLanguage === code ? 'selected' : ''}`}
              onClick={() => handleLanguageChange(code)}
            >
              <span className="language-flag">{config.flag}</span>
              <span className="language-name">{config.name}</span>
              {selectedLanguage === code && <span className="check-mark">✓</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Gender Selection */}
      <div className="setting-section">
        <label className="setting-label">
          <span className="label-icon">👤</span>
          Voice Gender
        </label>
        <div className="gender-options">
          <button
            className={`gender-option ${selectedGender === 'male' ? 'selected' : ''}`}
            onClick={() => handleGenderChange('male')}
          >
            <span className="gender-icon">👨</span>
            <span>Male</span>
            {selectedGender === 'male' && <span className="check-mark">✓</span>}
          </button>
          <button
            className={`gender-option ${selectedGender === 'female' ? 'selected' : ''}`}
            onClick={() => handleGenderChange('female')}
          >
            <span className="gender-icon">👩</span>
            <span>Female</span>
            {selectedGender === 'female' && <span className="check-mark">✓</span>}
          </button>
        </div>
      </div>

      {/* Voice Options */}
      <div className="setting-section">
        <label className="setting-label">
          <span className="label-icon">🔊</span>
          Available Voices
        </label>
        <div className="voice-options">
          {getAvailableVoicesForSelection().map((voice, index) => (
            <div
              key={index}
              className={`voice-option ${!voice.available ? 'unavailable' : ''} ${
                selectedVoice?.name.includes(voice.name) ? 'selected' : ''
              }`}
            >
              <div className="voice-info">
                <span className="voice-name">{voice.name}</span>
                <span className="voice-provider">{voice.provider}</span>
              </div>
              <div className="voice-status">
                {voice.available ? (
                  <>
                    <span className="quality-badge">{voice.quality}</span>
                    <span className="status-icon">✅</span>
                  </>
                ) : (
                  <>
                    <span className="unavailable-text">Not Installed</span>
                    <span className="status-icon">❌</span>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Voice Info */}
      {selectedVoice && (
        <div className="selected-voice-info">
          <div className="info-header">
            <span className="info-icon">✨</span>
            <span>Currently Selected</span>
          </div>
          <div className="info-content">
            <div className="info-row">
              <span className="info-label">Voice:</span>
              <span className="info-value">{selectedVoice.name}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Language:</span>
              <span className="info-value">{selectedVoice.lang}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Local:</span>
              <span className="info-value">{selectedVoice.localService ? 'Yes' : 'Cloud'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Test Voice Button */}
      <div className="setting-section">
        <button
          className={`test-voice-btn ${isTesting ? 'testing' : ''}`}
          onClick={handleTestVoice}
          disabled={!selectedVoice || isTesting}
        >
          {isTesting ? (
            <>
              <span className="spinner"></span>
              <span>Testing Voice...</span>
            </>
          ) : (
            <>
              <span className="btn-icon">🔊</span>
              <span>Test Voice</span>
            </>
          )}
        </button>
      </div>

      {/* Fallback Message */}
      {selectedLanguage === 'pa' && !getAvailableVoicesForSelection().some(v => v.available) && (
        <div className="fallback-message">
          <div className="message-icon">⚠️</div>
          <div className="message-content">
            <h4>Punjabi Voice Not Available</h4>
            <p>
              No Punjabi voices are currently installed on your system. 
              You can either:
            </p>
            <ul>
              <li>Install Punjabi language pack in Windows Settings</li>
              <li>Use OpenAI TTS for high-quality Punjabi voice (requires API key)</li>
              <li>The system will use a default voice as fallback</li>
            </ul>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="help-text">
        <p>
          💡 <strong>Tip:</strong> If your preferred voice is not available, 
          install the language pack from your operating system settings.
        </p>
      </div>
    </div>
  );
};

export default VoiceSettings;
