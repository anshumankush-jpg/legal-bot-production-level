import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './UserProfileMenu.css';

const UserProfileMenu = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 });
  const menuRef = useRef(null);
  const triggerRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target) &&
          triggerRef.current && !triggerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Calculate dropdown position when opened
  useEffect(() => {
    if (isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + 8,
        right: window.innerWidth - rect.right,
      });
    }
  }, [isOpen]);

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const handleLogout = () => {
    setIsOpen(false);
    if (onLogout) {
      onLogout();
    }
  };

  const handleMenuClick = (action) => {
    setIsOpen(false);
    switch(action) {
      case 'settings':
        break;
      case 'help':
        break;
      default:
        break;
    }
  };

  // Render dropdown using Portal to body
  const renderDropdown = () => {
    if (!isOpen) return null;

    return ReactDOM.createPortal(
      <>
        {/* Overlay */}
        <div 
          className="profile-menu-overlay"
          onClick={() => setIsOpen(false)}
        />
        
        {/* Dropdown Menu */}
        <div 
          ref={menuRef}
          className="profile-menu-dropdown"
          style={{
            top: `${dropdownPosition.top}px`,
            right: `${dropdownPosition.right}px`,
          }}
        >
          {/* User Section */}
          <div className="pmd-user-section">
            <div className="pmd-avatar">
              {user?.profile_photo_url ? (
                <img src={user.profile_photo_url} alt={user.name} />
              ) : (
                <span>{getInitials(user?.name)}</span>
              )}
            </div>
            <div className="pmd-user-info">
              <div className="pmd-user-name">{user?.name || 'User'}</div>
              <div className="pmd-user-email">{user?.email || ''}</div>
            </div>
          </div>

          <div className="pmd-divider"></div>

          {/* Menu Items */}
          <div className="pmd-menu-items">
            <button className="pmd-menu-item" onClick={() => handleMenuClick('personalization')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              <span>Personalization</span>
            </button>

            <button className="pmd-menu-item" onClick={() => handleMenuClick('settings')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <span>Settings</span>
            </button>

            <div className="pmd-divider"></div>

            <button className="pmd-menu-item" onClick={() => handleMenuClick('help')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <span>Help</span>
              <svg className="pmd-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>

            <div className="pmd-divider"></div>

            <button className="pmd-menu-item pmd-logout" onClick={handleLogout}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              <span>Log out</span>
            </button>
          </div>

          {/* Footer */}
          <div className="pmd-divider"></div>
          <div className="pmd-footer">
            <div className="pmd-footer-avatar">
              {user?.profile_photo_url ? (
                <img src={user.profile_photo_url} alt={user.name} />
              ) : (
                <span>{getInitials(user?.name)}</span>
              )}
            </div>
            <div className="pmd-footer-info">
              <div className="pmd-footer-name">{user?.name || 'User'}</div>
              <div className="pmd-footer-role">
                {user?.role === 'lawyer' ? 'Lawyer' : user?.role === 'employee_admin' ? 'Admin' : 'User'}
              </div>
            </div>
          </div>
        </div>
      </>,
      document.body
    );
  };

  return (
    <div className="user-profile-menu">
      <button 
        ref={triggerRef}
        className="profile-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
        title={`Logged in as ${user?.email || 'User'}`}
      >
        <div className="profile-avatar">
          {user?.profile_photo_url ? (
            <img src={user.profile_photo_url} alt={user.name} />
          ) : (
            <span className="profile-initials">{getInitials(user?.name)}</span>
          )}
        </div>
        <div className="profile-trigger-text">
          <div className="profile-trigger-name">{user?.name || 'User'}</div>
        </div>
        <div className="profile-chevron">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
            <path d="M6 8L2 4h8z"/>
          </svg>
        </div>
      </button>

      {renderDropdown()}
    </div>
  );
};

export default UserProfileMenu;
