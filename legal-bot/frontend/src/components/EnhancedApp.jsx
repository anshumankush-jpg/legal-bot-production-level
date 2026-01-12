import React, { useState, useEffect } from 'react';
import NavigationBar from './NavigationBar';
import ChatSidebar from './ChatSidebar';
import ChatInterface from './ChatInterface';
import RoleAccessBanner from './RoleAccessBanner';
import './EnhancedApp.css';

const EnhancedApp = () => {
  const [currentView, setCurrentView] = useState('chat');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [savedChats, setSavedChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [showAccessBanner, setShowAccessBanner] = useState(false);
  const [accessBannerInfo, setAccessBannerInfo] = useState(null);
  const [userRole, setUserRole] = useState('standard'); // guest, standard, premium, enterprise
  const [preferences, setPreferences] = useState(null);
  const [lawTypeSelection, setLawTypeSelection] = useState(null);
  const [showChatHistory, setShowChatHistory] = useState(false);

  // Load saved chats from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('legubot_chats');
    if (saved) {
      try {
        setSavedChats(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load saved chats', e);
      }
    }

    // Load user preferences
    const savedPrefs = localStorage.getItem('legubot_preferences');
    if (savedPrefs) {
      try {
        setPreferences(JSON.parse(savedPrefs));
      } catch (e) {
        console.error('Failed to load preferences', e);
      }
    }

    // Load law type selection
    const savedLawType = localStorage.getItem('legubot_law_type');
    if (savedLawType) {
      try {
        setLawTypeSelection(JSON.parse(savedLawType));
      } catch (e) {
        console.error('Failed to load law type', e);
      }
    }
  }, []);

  // Check API access based on role
  const checkApiAccess = async (apiName) => {
    try {
      const response = await fetch(`http://localhost:8000/api/auth/check-access?api_name=${apiName}`);
      const data = await response.json();
      
      if (!data.has_access) {
        setAccessBannerInfo({
          featureName: apiName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          requiredRole: data.required_role || 'premium',
          currentRole: userRole,
          upgradeInfo: data.upgrade_info
        });
        setShowAccessBanner(true);
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Failed to check API access:', error);
      return true; // Allow access if check fails
    }
  };

  const handleNewChat = () => {
    setCurrentChatId(null);
    setCurrentView('chat');
  };

  const handleLoadChat = (chatId) => {
    setCurrentChatId(chatId);
    setCurrentView('chat');
  };

  const handleDeleteChat = (chatId) => {
    const updated = savedChats.filter(c => c.id !== chatId);
    setSavedChats(updated);
    localStorage.setItem('legubot_chats', JSON.stringify(updated));
    
    if (currentChatId === chatId) {
      setCurrentChatId(null);
    }
  };

  const handleSearchChats = () => {
    setShowChatHistory(true);
  };

  const handleShowImages = async () => {
    const hasAccess = await checkApiAccess('image_gallery');
    if (hasAccess) {
      setCurrentView('images');
    }
  };

  const handleShowApps = () => {
    setCurrentView('apps');
  };

  const handleShowCodex = async () => {
    const hasAccess = await checkApiAccess('legal_codex');
    if (hasAccess) {
      setCurrentView('codex');
    }
  };

  const handleShowProjects = async () => {
    const hasAccess = await checkApiAccess('project_management');
    if (hasAccess) {
      setCurrentView('projects');
    }
  };

  const handleUpgrade = () => {
    // Redirect to upgrade page or show upgrade modal
    alert('Upgrade functionality coming soon! Contact sales for enterprise access.');
    setShowAccessBanner(false);
  };

  const handleResetPreferences = () => {
    setPreferences(null);
    setLawTypeSelection(null);
    localStorage.removeItem('legubot_preferences');
    localStorage.removeItem('legubot_law_type');
  };

  const handleChangeLawType = () => {
    setLawTypeSelection(null);
    localStorage.removeItem('legubot_law_type');
  };

  return (
    <div className="enhanced-app">
      <NavigationBar
        onNewChat={handleNewChat}
        onSearchChats={handleSearchChats}
        onShowImages={handleShowImages}
        onShowApps={handleShowApps}
        onShowCodex={handleShowCodex}
        onShowProjects={handleShowProjects}
        currentView={currentView}
      />

      <div className="app-body">
        <ChatSidebar
          savedChats={savedChats}
          currentChatId={currentChatId}
          onLoadChat={handleLoadChat}
          onNewChat={handleNewChat}
          onDeleteChat={handleDeleteChat}
          onSearchChats={handleSearchChats}
          isCollapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        <div className="main-content">
          {currentView === 'chat' && (
            <ChatInterface
              preferences={preferences}
              lawTypeSelection={lawTypeSelection}
              onResetPreferences={handleResetPreferences}
              onChangeLawType={handleChangeLawType}
            />
          )}

          {currentView === 'images' && (
            <div className="view-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <h2>Images & Documents</h2>
              <p>View all your uploaded images and documents</p>
            </div>
          )}

          {currentView === 'apps' && (
            <div className="view-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
              <h2>Legal Apps & Tools</h2>
              <p>Access specialized legal applications and utilities</p>
            </div>
          )}

          {currentView === 'codex' && (
            <div className="view-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <h2>Legal Codex</h2>
              <p>Browse statutes, regulations, and legal codes</p>
            </div>
          )}

          {currentView === 'projects' && (
            <div className="view-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
              <h2>Legal Projects</h2>
              <p>Manage your cases and legal projects</p>
            </div>
          )}
        </div>
      </div>

      {showAccessBanner && accessBannerInfo && (
        <RoleAccessBanner
          featureName={accessBannerInfo.featureName}
          requiredRole={accessBannerInfo.requiredRole}
          currentRole={accessBannerInfo.currentRole}
          upgradeInfo={accessBannerInfo.upgradeInfo}
          onUpgrade={handleUpgrade}
          onClose={() => setShowAccessBanner(false)}
        />
      )}
    </div>
  );
};

export default EnhancedApp;
