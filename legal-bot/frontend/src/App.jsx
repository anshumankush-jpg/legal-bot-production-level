import React, { useState, useEffect } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import OnboardingWizard from './components/OnboardingWizard'
import LawTypeSelector from './components/LawTypeSelector'
import RoleSelection from './components/RoleSelection'
import AuthPage from './components/AuthPage'
import OAuthCallback from './components/OAuthCallback'
import AccessDenied from './components/AccessDenied'
import NotProvisioned from './components/NotProvisioned'
import SettingsPage from './components/SettingsPage'
import PersonalizationPage from './components/PersonalizationPage'
import CookieConsentBanner from './components/CookieConsentBanner'
import { 
  HelpCenterPage, 
  ReleaseNotesPage, 
  TermsPage, 
  PrivacyPage, 
  KeyboardShortcutsPage,
  CookiePolicyPage
} from './components/HelpPages'

function App() {
  const [preferences, setPreferences] = useState(null);
  const [lawTypeSelection, setLawTypeSelection] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showLawSelector, setShowLawSelector] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isOAuthCallback, setIsOAuthCallback] = useState(false);
  const [currentPage, setCurrentPage] = useState('chat'); // chat, settings, personalization, help-center, etc.
  const [showCookieBanner, setShowCookieBanner] = useState(false);
  const [notProvisionedEmail, setNotProvisionedEmail] = useState('');
  const ensureDeviceId = () => {
    let deviceId = localStorage.getItem('device_id');
    if (!deviceId) {
      deviceId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : `device_${Date.now()}`;
      localStorage.setItem('device_id', deviceId);
    }
    return deviceId;
  };

  useEffect(() => {
    // Check if this is an OAuth callback
    const path = window.location.pathname;
    if (path.startsWith('/auth/callback/')) {
      setIsOAuthCallback(true);
      return;
    }

    // Check if this is access denied page
    if (path === '/access-denied') {
      return; // Don't redirect, show access denied
    }

    // Handle URL-based routing
    if (path === '/settings') setCurrentPage('settings');
    else if (path === '/personalization') setCurrentPage('personalization');
    else if (path === '/help') setCurrentPage('help-center');
    else if (path === '/terms') setCurrentPage('terms');
    else if (path === '/privacy') setCurrentPage('privacy');
    else if (path === '/keyboard-shortcuts') setCurrentPage('keyboard-shortcuts');
    else if (path === '/release-notes') setCurrentPage('release-notes');
    else if (path === '/cookies') setCurrentPage('cookies');
    else if (path === '/not-provisioned') setCurrentPage('not-provisioned');

    // Check if user is already authenticated
    const savedUser = localStorage.getItem('user');
    const savedToken = localStorage.getItem('access_token');
    
    if (savedUser && savedToken) {
      try {
        const userData = JSON.parse(savedUser);
        if (userData.is_provisioned === false) {
          setNotProvisionedEmail(userData.email || '');
          setCurrentPage('not-provisioned');
          return;
        }
        setUser(userData);
        setIsAuthenticated(true);
        setSelectedRole(userData.role || 'client');
        
        // Load preferences after auth
        loadPreferences();
      } catch (error) {
        console.error('Error loading user:', error);
        clearAuthState();
      }
    }

    // Check cookie consent
    const cookieConsent = localStorage.getItem('cookie_consent');
    if (!cookieConsent) {
      setShowCookieBanner(true);
    }
  }, []);

  const loadPreferences = () => {
    const savedPreferences = localStorage.getItem('plaza_ai_preferences');
    const savedLawType = localStorage.getItem('plaza_ai_law_type');
    
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setPreferences(prefs);
        setShowOnboarding(false);
        
        if (savedLawType) {
          const lawType = JSON.parse(savedLawType);
          setLawTypeSelection(lawType);
          setShowLawSelector(false);
        } else {
          setShowLawSelector(true);
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
        setShowOnboarding(true);
      }
    } else {
      setShowOnboarding(true);
    }
  };

  const clearAuthState = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    setSelectedRole(null);
  };

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    loadPreferences();
    // Add this account to device list for account switching
    const token = localStorage.getItem('access_token');
    if (token) {
      fetch('http://localhost:8000/api/profile/accounts/add', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Device-ID': ensureDeviceId()
        }
      }).catch(() => {});
    }
  };

  const handleBackToRoles = () => {
    setSelectedRole(null);
  };

  const handleLogout = () => {
    clearAuthState();
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
    setPreferences(null);
    setLawTypeSelection(null);
    setShowOnboarding(false);
    setShowLawSelector(false);
    setCurrentPage('chat');
  };

  const handleOnboardingComplete = (prefs) => {
    setPreferences(prefs);
    setShowOnboarding(false);
    setShowLawSelector(true);
  };

  const handleLawTypeComplete = (lawType) => {
    setLawTypeSelection(lawType);
    localStorage.setItem('plaza_ai_law_type', JSON.stringify(lawType));
    setShowLawSelector(false);
  };

  const handleResetPreferences = () => {
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
    setPreferences(null);
    setLawTypeSelection(null);
    setShowOnboarding(true);
    setShowLawSelector(false);
  };

  const handleChangeLawType = () => {
    localStorage.removeItem('plaza_ai_law_type');
    setLawTypeSelection(null);
    setShowLawSelector(true);
  };

  const handleBackToSettings = () => {
    localStorage.removeItem('plaza_ai_preferences');
    localStorage.removeItem('plaza_ai_law_type');
    setPreferences(null);
    setLawTypeSelection(null);
    setShowOnboarding(true);
    setShowLawSelector(false);
  };

  const handleNotProvisioned = (email) => {
    setNotProvisionedEmail(email || '');
    setCurrentPage('not-provisioned');
    window.history.pushState({}, '', '/not-provisioned');
  };

  // Navigation handler for account menu
  const handleNavigate = (page) => {
    setCurrentPage(page);
    // Update URL without reload
    const pathMap = {
      'chat': '/',
      'settings': '/settings',
      'personalization': '/personalization',
      'help-center': '/help',
      'release-notes': '/release-notes',
      'terms': '/terms',
      'privacy': '/privacy',
      'keyboard-shortcuts': '/keyboard-shortcuts',
      'cookies': '/cookies'
    };
    window.history.pushState({}, '', pathMap[page] || '/');
  };

  const handleBackToChat = () => {
    setCurrentPage('chat');
    window.history.pushState({}, '', '/');
  };

  const handleProfileUpdate = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const handleCookieConsent = (consent) => {
    setShowCookieBanner(false);
    console.log('Cookie consent:', consent);
  };

  // Handle access denied
  if (window.location.pathname === '/access-denied') {
    return <AccessDenied />;
  }

  // Handle OAuth callback
  if (isOAuthCallback) {
    return (
      <OAuthCallback 
        onAuthSuccess={(userData) => {
          setUser(userData);
          setIsAuthenticated(true);
          setSelectedRole(userData.role || 'client');
          setIsOAuthCallback(false);
          // Clear URL and redirect to home
          window.history.replaceState({}, document.title, '/');
          loadPreferences();
        }} 
      />
    );
  }

  // Step 1: Show role selection if no role selected
  if (!selectedRole) {
    return (
      <>
        <RoleSelection onRoleSelect={handleRoleSelect} />
        {showCookieBanner && (
          <CookieConsentBanner user={null} onAccept={handleCookieConsent} />
        )}
      </>
    );
  }

  // Step 2: Show auth page if not authenticated
  if (!isAuthenticated) {
    return (
      <div style={{ position: 'relative' }}>
        <button 
          onClick={handleBackToRoles}
          style={{
            position: 'absolute',
            top: '24px',
            left: '24px',
            background: 'rgba(0, 0, 0, 0.3)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#8892b0',
            padding: '12px 20px',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: 100,
            backdropFilter: 'blur(10px)',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => {
            e.target.style.background = 'rgba(0, 212, 255, 0.1)';
            e.target.style.borderColor = '#00d4ff';
            e.target.style.color = '#00d4ff';
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'rgba(0, 0, 0, 0.3)';
            e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            e.target.style.color = '#8892b0';
          }}
        >
          ← Back to Role Selection
        </button>
        <AuthPage role={selectedRole} onAuthSuccess={handleAuthSuccess} onNotProvisioned={handleNotProvisioned} />
        {showCookieBanner && (
          <CookieConsentBanner user={null} onAccept={handleCookieConsent} />
        )}
      </div>
    );
  }

  // Step 3: Show onboarding wizard
  if (showOnboarding || !preferences) {
    return (
      <>
        <OnboardingWizard onComplete={handleOnboardingComplete} userRole={selectedRole} />
        {showCookieBanner && (
          <CookieConsentBanner user={user} onAccept={handleCookieConsent} />
        )}
      </>
    );
  }

  // Step 4: Show law type selector
  if (showLawSelector || !lawTypeSelection) {
    return (
      <>
        <LawTypeSelector 
          preferences={preferences} 
          onComplete={handleLawTypeComplete}
          onBack={handleBackToSettings}
          userRole={selectedRole}
        />
        {showCookieBanner && (
          <CookieConsentBanner user={user} onAccept={handleCookieConsent} />
        )}
      </>
    );
  }

  // Step 5: Render current page
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'not-provisioned':
        return <NotProvisioned email={notProvisionedEmail} />;
      case 'settings':
        return (
          <SettingsPage 
            user={user} 
            onBack={handleBackToChat}
            onProfileUpdate={handleProfileUpdate}
          />
        );
      case 'personalization':
        return (
          <PersonalizationPage 
            user={user} 
            onBack={handleBackToChat}
          />
        );
      case 'help-center':
        return <HelpCenterPage onBack={handleBackToChat} />;
      case 'release-notes':
        return <ReleaseNotesPage onBack={handleBackToChat} />;
      case 'cookies':
        return <CookiePolicyPage onBack={handleBackToChat} />;
      case 'terms':
        return <TermsPage onBack={handleBackToChat} />;
      case 'privacy':
        return <PrivacyPage onBack={handleBackToChat} />;
      case 'keyboard-shortcuts':
        return <KeyboardShortcutsPage onBack={handleBackToChat} />;
      default:
        return (
          <ChatInterface 
            preferences={preferences}
            lawTypeSelection={lawTypeSelection}
            onResetPreferences={handleResetPreferences}
            onChangeLawType={handleChangeLawType}
            user={user}
            onLogout={handleLogout}
            onNavigate={handleNavigate}
          />
        );
    }
  };

  return (
    <>
      {renderCurrentPage()}
      {showCookieBanner && (
        <CookieConsentBanner user={user} onAccept={handleCookieConsent} />
      )}
    </>
  );
}

export default App
