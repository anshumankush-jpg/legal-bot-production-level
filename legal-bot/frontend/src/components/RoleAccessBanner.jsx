import React from 'react';
import './RoleAccessBanner.css';

const RoleAccessBanner = ({ 
  featureName, 
  requiredRole, 
  currentRole = 'guest',
  upgradeInfo,
  onUpgrade,
  onClose 
}) => {
  const roleColors = {
    guest: '#9ca3af',
    standard: '#3b82f6',
    premium: '#8b5cf6',
    enterprise: '#f59e0b'
  };

  const roleIcons = {
    guest: '👤',
    standard: '⭐',
    premium: '💎',
    enterprise: '👑'
  };

  return (
    <div className="role-access-banner">
      <div className="banner-content">
        <div className="banner-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        </div>

        <div className="banner-text">
          <h3>{featureName} Requires Upgrade</h3>
          <p>
            This feature requires <strong style={{ color: roleColors[requiredRole] }}>
              {roleIcons[requiredRole]} {requiredRole.toUpperCase()}
            </strong> access or higher.
          </p>
          <p className="current-role">
            Your current role: <strong style={{ color: roleColors[currentRole] }}>
              {roleIcons[currentRole]} {currentRole.toUpperCase()}
            </strong>
          </p>

          {upgradeInfo && (
            <div className="upgrade-details">
              <h4>Upgrade Benefits:</h4>
              <ul>
                {upgradeInfo.benefits?.map((benefit, index) => (
                  <li key={index}>✓ {benefit}</li>
                ))}
              </ul>
              {upgradeInfo.price && (
                <p className="pricing">
                  Starting at <strong>${upgradeInfo.price}/month</strong>
                </p>
              )}
            </div>
          )}
        </div>

        <div className="banner-actions">
          {onUpgrade && (
            <button className="upgrade-btn" onClick={onUpgrade}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="19" x2="12" y2="5"></line>
                <polyline points="5 12 12 5 19 12"></polyline>
              </svg>
              Upgrade Now
            </button>
          )}
          {onClose && (
            <button className="close-btn" onClick={onClose}>
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoleAccessBanner;
