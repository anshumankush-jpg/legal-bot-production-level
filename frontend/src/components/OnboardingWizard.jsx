import React, { useState } from 'react';
import './OnboardingWizard.css';

const OnboardingWizard = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [showMoreLanguages, setShowMoreLanguages] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedProvince, setSelectedProvince] = useState(null);

  // Main languages (first page)
  const mainLanguages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' }
  ];

  // Additional languages (more options)
  const additionalLanguages = [
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'pa', name: 'Punjabi', flag: '🇮🇳' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳' }
  ];

  // Canadian provinces
  const canadianProvinces = [
    { code: 'ON', name: 'Ontario' },
    { code: 'BC', name: 'British Columbia' },
    { code: 'AB', name: 'Alberta' },
    { code: 'QC', name: 'Quebec' },
    { code: 'MB', name: 'Manitoba' },
    { code: 'SK', name: 'Saskatchewan' },
    { code: 'NS', name: 'Nova Scotia' },
    { code: 'NB', name: 'New Brunswick' },
    { code: 'NL', name: 'Newfoundland and Labrador' },
    { code: 'PE', name: 'Prince Edward Island' },
    { code: 'NT', name: 'Northwest Territories' },
    { code: 'YT', name: 'Yukon' },
    { code: 'NU', name: 'Nunavut' }
  ];

  // US States
  const usStates = [
    { code: 'AL', name: 'Alabama' },
    { code: 'AK', name: 'Alaska' },
    { code: 'AZ', name: 'Arizona' },
    { code: 'AR', name: 'Arkansas' },
    { code: 'CA', name: 'California' },
    { code: 'CO', name: 'Colorado' },
    { code: 'CT', name: 'Connecticut' },
    { code: 'DE', name: 'Delaware' },
    { code: 'FL', name: 'Florida' },
    { code: 'GA', name: 'Georgia' },
    { code: 'HI', name: 'Hawaii' },
    { code: 'ID', name: 'Idaho' },
    { code: 'IL', name: 'Illinois' },
    { code: 'IN', name: 'Indiana' },
    { code: 'IA', name: 'Iowa' },
    { code: 'KS', name: 'Kansas' },
    { code: 'KY', name: 'Kentucky' },
    { code: 'LA', name: 'Louisiana' },
    { code: 'ME', name: 'Maine' },
    { code: 'MD', name: 'Maryland' },
    { code: 'MA', name: 'Massachusetts' },
    { code: 'MI', name: 'Michigan' },
    { code: 'MN', name: 'Minnesota' },
    { code: 'MS', name: 'Mississippi' },
    { code: 'MO', name: 'Missouri' },
    { code: 'MT', name: 'Montana' },
    { code: 'NE', name: 'Nebraska' },
    { code: 'NV', name: 'Nevada' },
    { code: 'NH', name: 'New Hampshire' },
    { code: 'NJ', name: 'New Jersey' },
    { code: 'NM', name: 'New Mexico' },
    { code: 'NY', name: 'New York' },
    { code: 'NC', name: 'North Carolina' },
    { code: 'ND', name: 'North Dakota' },
    { code: 'OH', name: 'Ohio' },
    { code: 'OK', name: 'Oklahoma' },
    { code: 'OR', name: 'Oregon' },
    { code: 'PA', name: 'Pennsylvania' },
    { code: 'RI', name: 'Rhode Island' },
    { code: 'SC', name: 'South Carolina' },
    { code: 'SD', name: 'South Dakota' },
    { code: 'TN', name: 'Tennessee' },
    { code: 'TX', name: 'Texas' },
    { code: 'UT', name: 'Utah' },
    { code: 'VT', name: 'Vermont' },
    { code: 'VA', name: 'Virginia' },
    { code: 'WA', name: 'Washington' },
    { code: 'WV', name: 'West Virginia' },
    { code: 'WI', name: 'Wisconsin' },
    { code: 'WY', name: 'Wyoming' }
  ];

  const handleLanguageSelect = (lang) => {
    setSelectedLanguage(lang);
    setStep(2);
  };

  const handleCountrySelect = (country) => {
    setSelectedCountry(country);
    if (country === 'CA') {
      setStep(3); // Go to province selection for Canada
    } else {
      // For USA, we might want to ask for state, but for now, complete
      completeOnboarding(country, null);
    }
  };

  const handleProvinceSelect = (province) => {
    setSelectedProvince(province);
    completeOnboarding(selectedCountry, province);
  };

  const completeOnboarding = (country, province) => {
    const preferences = {
      language: selectedLanguage,
      country: country,
      province: province,
      timestamp: new Date().toISOString()
    };

    // Store in localStorage
    localStorage.setItem('plaza_ai_preferences', JSON.stringify(preferences));

    // Call completion callback
    onComplete(preferences);
  };

  const handleBack = () => {
    if (step === 2) {
      setStep(1);
      setSelectedCountry(null);
    } else if (step === 3) {
      setStep(2);
      setSelectedProvince(null);
    }
  };

  return (
    <div className="onboarding-wizard">
      <div className="wizard-container">
        <div className="wizard-header">
          <div className="logo">
            <span className="logo-icon">⚖️</span>
            <h1>PLAZA-AI</h1>
          </div>
          <p className="wizard-subtitle">Legal Assistant Setup</p>
        </div>

        <div className="wizard-progress">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <div className="step-circle">1</div>
            <span>Language</span>
          </div>
          <div className={`progress-line ${step >= 2 ? 'active' : ''}`}></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <div className="step-circle">2</div>
            <span>Country</span>
          </div>
          {selectedCountry === 'CA' && (
            <>
              <div className={`progress-line ${step >= 3 ? 'active' : ''}`}></div>
              <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
                <div className="step-circle">3</div>
                <span>Province</span>
              </div>
            </>
          )}
        </div>

        <div className="wizard-content">
          {/* Step 1: Language Selection */}
          {step === 1 && (
            <div className="wizard-step">
              <h2>Select Your Language</h2>
              <p className="step-description">Choose your preferred language for legal assistance</p>
              
              <div className="language-grid">
                {mainLanguages.map((lang) => (
                  <button
                    key={lang.code}
                    className={`language-card ${selectedLanguage?.code === lang.code ? 'selected' : ''}`}
                    onClick={() => handleLanguageSelect(lang)}
                  >
                    <span className="language-flag">{lang.flag}</span>
                    <span className="language-name">{lang.name}</span>
                  </button>
                ))}
              </div>

              {/* More Options Button */}
              <button
                className="more-options-btn"
                onClick={() => setShowMoreLanguages(!showMoreLanguages)}
              >
                <span className="plus-icon">+</span>
                <span>More Options</span>
              </button>

              {/* Additional Languages */}
              {showMoreLanguages && (
                <div className="additional-languages">
                  <h3>Additional Languages</h3>
                  <div className="language-grid">
                    {additionalLanguages.map((lang) => (
                      <button
                        key={lang.code}
                        className={`language-card ${selectedLanguage?.code === lang.code ? 'selected' : ''}`}
                        onClick={() => handleLanguageSelect(lang)}
                      >
                        <span className="language-flag">{lang.flag}</span>
                        <span className="language-name">{lang.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Country Selection */}
          {step === 2 && (
            <div className="wizard-step">
              <h2>Select Your Country</h2>
              <p className="step-description">Choose your country to access relevant legal information</p>
              
              <div className="country-grid">
                <button
                  className={`country-card ${selectedCountry === 'CA' ? 'selected' : ''}`}
                  onClick={() => handleCountrySelect('CA')}
                >
                  <span className="country-flag">🇨🇦</span>
                  <span className="country-name">Canada</span>
                </button>
                <button
                  className={`country-card ${selectedCountry === 'US' ? 'selected' : ''}`}
                  onClick={() => handleCountrySelect('US')}
                >
                  <span className="country-flag">🇺🇸</span>
                  <span className="country-name">United States</span>
                </button>
              </div>

              <button className="back-btn" onClick={handleBack}>
                ← Back
              </button>
            </div>
          )}

          {/* Step 3: Province Selection (Canada only) */}
          {step === 3 && selectedCountry === 'CA' && (
            <div className="wizard-step">
              <h2>Select Your Province</h2>
              <p className="step-description">Choose your province for province-specific legal information</p>
              
              <div className="province-grid">
                {canadianProvinces.map((province) => (
                  <button
                    key={province.code}
                    className={`province-card ${selectedProvince === province.code ? 'selected' : ''}`}
                    onClick={() => handleProvinceSelect(province.code)}
                  >
                    <span className="province-name">{province.name}</span>
                    <span className="province-code">{province.code}</span>
                  </button>
                ))}
              </div>

              <button className="back-btn" onClick={handleBack}>
                ← Back
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;