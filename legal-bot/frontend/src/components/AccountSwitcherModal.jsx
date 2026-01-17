import React, { useEffect, useState } from 'react';
import './AccountSwitcherModal.css';

const API_URL = 'http://localhost:8000';

const getDeviceId = () => {
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    deviceId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : `device_${Date.now()}`;
    localStorage.setItem('device_id', deviceId);
  }
  return deviceId;
};

const AccountSwitcherModal = ({ isOpen, onClose, onSwitched, onAddAccount }) => {
  const [accounts, setAccounts] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    if (!isOpen) return;
    const loadAccounts = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_URL}/api/profile/accounts`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-Device-ID': getDeviceId()
          }
        });
        const data = await response.json();
        setAccounts(data.accounts || []);
        setCurrentUserId(data.current_user_id || null);
      } catch (error) {
        console.error('Failed to load accounts:', error);
      }
    };
    loadAccounts();
  }, [isOpen]);

  const handleSwitch = async (userId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile/accounts/switch/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Device-ID': getDeviceId()
        }
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to switch account');
      }
      localStorage.setItem('access_token', data.token.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      onSwitched && onSwitched(data.user);
      onClose();
    } catch (error) {
      console.error('Switch account error:', error);
    }
  };

  const handleRemove = async (userId) => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch(`${API_URL}/api/profile/accounts/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Device-ID': getDeviceId()
        }
      });
      setAccounts(prev => prev.filter(acc => acc.user_id !== userId));
    } catch (error) {
      console.error('Remove account error:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="account-switcher-overlay">
      <div className="account-switcher-modal">
        <div className="account-switcher-header">
          <h3>Accounts</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="account-list">
          {accounts.map(account => (
            <div key={account.user_id} className={`account-item ${account.user_id === currentUserId ? 'active' : ''}`}>
              <div className="account-avatar">
                {account.avatar_url ? (
                  <img src={account.avatar_url} alt={account.display_name || account.name} />
                ) : (
                  <span>{(account.display_name || account.name || account.email || 'U').charAt(0).toUpperCase()}</span>
                )}
              </div>
              <div className="account-info">
                <div className="account-name">{account.display_name || account.name || account.email}</div>
                <div className="account-email">{account.email}</div>
              </div>
              <div className="account-actions">
                {account.user_id !== currentUserId && (
                  <button onClick={() => handleSwitch(account.user_id)}>Switch</button>
                )}
                <button className="remove-btn" onClick={() => handleRemove(account.user_id)}>Remove</button>
              </div>
            </div>
          ))}
        </div>
        <div className="account-switcher-footer">
          <button className="add-account-btn" onClick={onAddAccount}>Add account</button>
        </div>
      </div>
    </div>
  );
};

export default AccountSwitcherModal;
