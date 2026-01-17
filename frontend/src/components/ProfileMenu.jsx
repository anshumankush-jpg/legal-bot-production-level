import React, { useState, useEffect, useRef } from 'react';
import './ProfileMenu.css';

const ProfileMenu = ({ user, onLogout, onViewChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [profile, setProfile] = useState(null);
  const menuRef = useRef(null);
  const buttonRef = useRef(null);

  useEffect(() => {
    // Load profile data when user is available
    if (user) {
      loadProfile();
    }
  }, [user]);

  useEffect(() => {
    // Close menu when clicking outside
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target) &&
          buttonRef.current && !buttonRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadProfile = async () => {
    try {
      const response = await fetch('/api/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleMenuItemClick = (action) => {
    setIsOpen(false);
    switch (action) {
      case 'upgrade':
        onViewChange && onViewChange('upgrade');
        break;
      case 'personalization':
        onViewChange && onViewChange('personalization');
        break;
      case 'settings':
        onViewChange && onViewChange('settings');
        break;
      case 'help':
        onViewChange && onViewChange('help');
        break;
      case 'logout':
        onLogout && onLogout();
        break;
      default:
        break;
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const getUserHandle = (name, email) => {
    if (!name && !email) return '@user';
    if (name) {
      return '@' + name.toLowerCase().replace(/\s+/g, '');
    }
    return '@' + email.split('@')[0];
  };

  if (!user) {
    // Default user for demo purposes
    const defaultUser = {
      name: 'anshumankush',
      email: 'anshumankush@example.com',
      role: 'plus'
    };
    user = defaultUser;
  }

  const displayName = profile?.display_name || user.name || 'User';
  const avatarUrl = profile?.avatar_url;
  const userHandle = getUserHandle(displayName, user.email);
  const isPlusUser = user.role === 'plus' || user.subscription === 'plus';

  return (
    <div className="profile-menu-wrapper">
      <button
        ref={buttonRef}
        className="profile-menu-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
        aria-expanded={isOpen}
      >
        <div className="profile-menu-avatar">
          {avatarUrl ? (
            <img src={avatarUrl} alt={displayName} />
          ) : (
            <div className="profile-menu-initials">
              {getInitials(displayName)}
            </div>
          )}
        </div>
      </button>

      {isOpen && (
        <div className="profile-menu-dropdown" ref={menuRef}>
          <div className="profile-menu-header">
            <div className="profile-menu-header-avatar">
              {avatarUrl ? (
                <img src={avatarUrl} alt={displayName} />
              ) : (
                <div className="profile-menu-initials">
                  {getInitials(displayName)}
                </div>
              )}
            </div>
            <div className="profile-menu-header-info">
              <div className="profile-menu-name">{displayName}</div>
              <div className="profile-menu-handle">{userHandle}</div>
            </div>
          </div>

          {isPlusUser && (
            <div className="profile-menu-badge">
              <div className="profile-menu-user-info">
                <div className="profile-menu-user-avatar">
                  {avatarUrl ? (
                    <img src={avatarUrl} alt={displayName} />
                  ) : (
                    <div className="profile-menu-initials-small">
                      {getInitials(displayName)}
                    </div>
                  )}
                </div>
                <div className="profile-menu-user-details">
                  <div className="profile-menu-user-name">Anshuman Kush</div>
                  <div className="profile-menu-user-tier">Plus</div>
                </div>
              </div>
            </div>
          )}

          <div className="profile-menu-divider"></div>

          <div className="profile-menu-items">
            <button 
              className="profile-menu-item"
              onClick={() => handleMenuItemClick('upgrade')}
            >
              <svg className="profile-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
              <span>Upgrade plan</span>
            </button>

            <button 
              className="profile-menu-item"
              onClick={() => handleMenuItemClick('personalization')}
            >
              <svg className="profile-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>Personalization</span>
            </button>

            <button 
              className="profile-menu-item"
              onClick={() => handleMenuItemClick('settings')}
            >
              <svg className="profile-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6"></path>
                <path d="M17 12h-2m-6 0H7"></path>
              </svg>
              <span>Settings</span>
            </button>

            <div className="profile-menu-divider"></div>

            <button 
              className="profile-menu-item"
              onClick={() => handleMenuItemClick('help')}
            >
              <svg className="profile-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <span>Help</span>
              <svg className="profile-menu-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>

            <div className="profile-menu-divider"></div>

            <button 
              className="profile-menu-item"
              onClick={() => handleMenuItemClick('logout')}
            >
              <svg className="profile-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              <span>Log out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileMenu;
