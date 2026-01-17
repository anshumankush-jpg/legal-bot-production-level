import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './OnboardingWizard.css';

const OnboardingWizard = ({ onComplete }) => {
  const { user, logout } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  // Get user initials
  const getUserInitials = () => {
    if (!user?.name) return '?';
    const parts = user.name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };
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
    setStep(3); // Go to province/state selection for both countries
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
      {/* Profile Badge - Always visible at top right */}
      <div className="onboarding-profile-section">
        <button 
          className="profile-badge" 
          onClick={() => setShowProfileMenu(!showProfileMenu)}
          title="Profile & Settings"
        >
          {user?.picture ? (
            <img src={user.picture} alt="Profile" className="profile-badge-img" />
          ) : (
            <div className="profile-badge-initials">{getUserInitials()}</div>
          )}
          <span className="profile-badge-name">{user?.name || user?.email?.split('@')[0] || 'User'}</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>

        {showProfileMenu && (
          <div className="profile-dropdown-menu">
            <div className="profile-dropdown-header">
              {user?.picture ? (
                <img src={user.picture} alt="Profile" className="profile-dropdown-img" />
              ) : (
                <div className="profile-dropdown-initials">{getUserInitials()}</div>
              )}
              <div className="profile-dropdown-info">
                <div className="profile-dropdown-name">{user?.name || 'User'}</div>
                <div className="profile-dropdown-email">{user?.email || ''}</div>
              </div>
            </div>
            <div className="profile-dropdown-divider"></div>
            <button className="profile-dropdown-item" onClick={logout}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              <span>Log out</span>
            </button>
          </div>
        )}
      </div>

      <div className="wizard-container">
        <div className="wizard-header">
          <div className="logo">
            <h1 className="logo-text">LEGID</h1>
          </div>
          <p className="wizard-subtitle">Your Advanced Legal Intelligence Assistant</p>
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

          {/* Step 3: Province/State Selection */}
          {step === 3 && (
            <div className="wizard-step">
              <h2>Select Your {selectedCountry === 'CA' ? 'Province' : 'State'}</h2>
              <p className="step-description">
                Choose your {selectedCountry === 'CA' ? 'province' : 'state'} for jurisdiction-specific legal information
              </p>
              
              <div className="province-grid">
                {(selectedCountry === 'CA' ? canadianProvinces : usStates).map((region) => (
                  <button
                    key={region.code}
                    className={`province-card ${selectedProvince === region.code ? 'selected' : ''}`}
                    onClick={() => handleProvinceSelect(region.code)}
                  >
                    <span className="province-name">{region.name}</span>
                    <span className="province-code">{region.code}</span>
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