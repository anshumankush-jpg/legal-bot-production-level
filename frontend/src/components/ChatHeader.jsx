import React from 'react';
import './ChatHeader.css';

const ChatHeader = ({ 
  preferences,
  user,
  lawTypeSelection, 
  onNewChat,
  onChangeLawType,
  onResetPreferences,
  onShowRecentUpdates,
  onShowCaseLookup,
  onShowAmendmentGenerator,
  onShowDocumentGenerator,
  onShowChatHistory,
  onShowSettings,
  onShowAISummary,
  onShowQuickSummary
}) => {
  const getStoredUser = () => {
    try {
      const raw =
        localStorage.getItem('user_data') ||
        localStorage.getItem('legid_user') ||
        localStorage.getItem('auth_user');
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed?.user || parsed;
    } catch {
      return null;
    }
  };

  const getResolvedUser = () => {
    return user || getStoredUser() || preferences?.user || null;
  };

  const getUserName = () => {
    const resolved = getResolvedUser();
    return (
      resolved?.display_name ||
      resolved?.name ||
      resolved?.email ||
      preferences?.userName ||
      'User'
    );
  };

  const getUserInitials = () => {
    const name = getUserName();
    if (!name) return 'U';
    const base = name.includes('@') ? name.split('@')[0] : name;
    return base
      .split(' ')
      .filter(Boolean)
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getLawType = () => {
    return lawTypeSelection?.lawType || 'Wills, Estates, and Trusts';
  };

  const getLanguage = () => {
    return preferences?.language?.name || 'English';
  };

  const getCountry = () => {
    return preferences?.country === 'CA' ? 'Canada' : 'United States';
  };

  const getProvince = () => {
    return preferences?.province || 'ON';
  };

  return (
    <div className="header-container">
      {/* Row 1: Top Bar */}
      <div className="header-top">
        <div className="top-left">
          <div className="brand-row">
            <span className="brand-mark">⚖️</span>
            <span className="legid-text">LEGID</span>
          </div>
        </div>

        <div className="top-right">
          <button className="profile-pill">
            <div className="avatar">{getUserInitials()}</div>
            <span className="user-name">{getUserName()}</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <span className="andy-status">Andy OFF</span>
          <span className="english-badge">English</span>

          <div className="offence-input">
            <label>Offence Number (optional):</label>
            <input type="text" placeholder="e.g., 123456789" />
          </div>
        </div>
      </div>

      {/* Row 2: Info Line */}
      <div className="header-info">
        <span>Language: {getLanguage()}</span>
        <span>{getCountry()}</span>
        <span>{getProvince()}</span>
        <span className="law-type">{getLawType()}</span>
      </div>

    </div>
  );
};

export default ChatHeader;
