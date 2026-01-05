import React, { useState, useEffect } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import OnboardingWizard from './components/OnboardingWizard'

function App() {
  const [preferences, setPreferences] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);

  useEffect(() => {
    // Check if preferences exist in localStorage
    const savedPreferences = localStorage.getItem('plaza_ai_preferences');
    if (savedPreferences) {
      try {
        const prefs = JSON.parse(savedPreferences);
        setPreferences(prefs);
        setShowOnboarding(false);
      } catch (error) {
        console.error('Error loading preferences:', error);
        // If error, show onboarding
        setShowOnboarding(true);
      }
    }
  }, []);

  const handleOnboardingComplete = (prefs) => {
    setPreferences(prefs);
    setShowOnboarding(false);
  };

  const handleResetPreferences = () => {
    localStorage.removeItem('plaza_ai_preferences');
    setPreferences(null);
    setShowOnboarding(true);
  };

  if (showOnboarding) {
    return <OnboardingWizard onComplete={handleOnboardingComplete} />;
  }

  return <ChatInterface preferences={preferences} onResetPreferences={handleResetPreferences} />;
}

export default App
