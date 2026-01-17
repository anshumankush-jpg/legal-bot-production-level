import React, { useState, useEffect } from 'react'
import './App.css'
import { useAuth } from './context/AuthContext'
import LoginPage from './components/LoginPage'
import ChatInterface from './components/ChatInterface'
import OnboardingWizard from './components/OnboardingWizard'
import LawTypeSelector from './components/LawTypeSelector'

function App() {
  const { isAuthenticated, loading, user } = useAuth();
  const [preferences, setPreferences] = useState(null);
  const [lawTypeSelection, setLawTypeSelection] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [showLawSelector, setShowLawSelector] = useState(false);

  useEffect(() => {
    // Only check preferences if user is authenticated
    if (!isAuthenticated) return;

    // Check if preferences exist in localStorage
    const savedPreferences = localStorage.getItem('plaza_ai_preferences');
    const savedLawType = localStorage.getItem('plaza_ai_law_type');
    
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setPreferences(prefs);
        setShowOnboarding(false);
        
        // Check if law type is saved
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
    }
  }, [isAuthenticated]);

  const handleOnboardingComplete = (prefs) => {
    setPreferences(prefs);
    setShowOnboarding(false);
    setShowLawSelector(true); // Go directly to law selector after onboarding
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

  // Show loading state
  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner-large"></div>
        <p>Loading LEGID...</p>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Show onboarding first (after login)
  if (showOnboarding) {
    return <OnboardingWizard onComplete={handleOnboardingComplete} />;
  }

  // Then show law type selector
  if (showLawSelector || !lawTypeSelection) {
    return <LawTypeSelector 
      preferences={preferences} 
      onComplete={handleLawTypeComplete}
      onBack={handleBackToSettings}
    />;
  }

  // Finally show chat interface with welcome message
  // Pass user info to ChatInterface
  return (
    <ChatInterface 
      preferences={preferences}
      lawTypeSelection={lawTypeSelection}
      onResetPreferences={handleResetPreferences}
      onChangeLawType={handleChangeLawType}
      user={user}
    />
  );
}

export default App
