import React from 'react';
import './RoleSelection.css';

const RoleSelection = ({ onRoleSelect }) => {
  const roles = [
    {
      id: 'client',
      title: 'Continue as User',
      description: 'Access legal information, get AI-powered legal assistance, and manage your documents',
      icon: '👤',
      gradient: 'linear-gradient(135deg, #00d4ff 0%, #0099cc 100%)'
    },
    {
      id: 'lawyer',
      title: 'Continue as Lawyer',
      description: 'Manage client matters, grant employee access, and access advanced legal tools',
      icon: '⚖️',
      gradient: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%)'
    }
  ];

  return (
    <div className="role-selection-container">
      <div className="role-selection-content">
        <div className="role-selection-header">
          <h1 className="role-selection-title">LEGID</h1>
          <p className="role-selection-subtitle">
            Advanced Legal Intelligence & Document Generator
          </p>
        </div>

        <div className="role-cards-container">
          {roles.map((role) => (
            <div
              key={role.id}
              className="role-card"
              onClick={() => onRoleSelect(role.id)}
            >
              <div className="role-card-glow" style={{ background: role.gradient }}></div>
              <div className="role-card-content">
                <div className="role-card-icon">
                  {role.icon}
                </div>
                <h2 className="role-card-title">{role.title}</h2>
                <p className="role-card-description">{role.description}</p>
                <button
                  className="role-card-button"
                  style={{ background: role.gradient }}
                >
                  Get Started →
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="role-selection-footer">
          <p className="support-info">
            Need help? Contact{' '}
            <a href="mailto:info@predictivetechlabs.com">
              info@predictivetechlabs.com
            </a>
          </p>
          <p className="legal-disclaimer">
            ⚠️ This application provides legal information only, not legal advice.
            Always consult a licensed attorney for legal advice.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RoleSelection;
