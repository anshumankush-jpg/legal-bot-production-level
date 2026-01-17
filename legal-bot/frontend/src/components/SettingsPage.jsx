import React, { useState, useEffect } from 'react';
import './SettingsPage.css';

const API_URL = 'http://localhost:8000';

const SettingsPage = ({ user, onBack, onProfileUpdate }) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  
  // Profile form state
  const [profile, setProfile] = useState({
    display_name: '',
    username: '',
    avatar_url: '',
    phone: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    province_state: '',
    postal_zip: '',
    country: ''
  });
  const [avatarPreview, setAvatarPreview] = useState('');
  const [avatarFile, setAvatarFile] = useState(null);

  // Consent state
  const [consent, setConsent] = useState({
    analytics: false,
    marketing: false,
    functional: true
  });

  useEffect(() => {
    loadProfile();
    loadConsent();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProfile({
          display_name: data.profile?.display_name || data.name || '',
          username: data.profile?.username || '',
          avatar_url: data.profile?.avatar_url || '',
          phone: data.profile?.phone || '',
          address_line_1: data.profile?.address?.line_1 || '',
          address_line_2: data.profile?.address?.line_2 || '',
          city: data.profile?.address?.city || '',
          province_state: data.profile?.address?.province_state || '',
          postal_zip: data.profile?.address?.postal_zip || '',
          country: data.profile?.address?.country || ''
        });
        setAvatarPreview(data.profile?.avatar_url || '');
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadConsent = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile/consent`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setConsent({
          analytics: data.analytics || false,
          marketing: data.marketing || false,
          functional: data.functional !== false
        });
      }
    } catch (error) {
      console.error('Error loading consent:', error);
    }
  };

  const handleProfileChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      setMessage({ type: 'error', text: 'Unsupported file type. Use PNG, JPG, or WEBP.' });
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'File too large. Max 5MB.' });
      return;
    }
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const uploadAvatar = async () => {
    if (!avatarFile) return;
    try {
      setSaving(true);
      setMessage(null);
      const token = localStorage.getItem('access_token');
      const filename = encodeURIComponent(avatarFile.name);
      const contentType = encodeURIComponent(avatarFile.type);
      const urlResponse = await fetch(
        `${API_URL}/api/profile/avatar/upload-url?filename=${filename}&content_type=${contentType}`,
        { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }
      );
      const urlData = await urlResponse.json();
      if (!urlResponse.ok) {
        throw new Error(urlData.detail || 'Failed to get upload URL');
      }

      await fetch(urlData.signed_url, {
        method: 'PUT',
        headers: { 'Content-Type': avatarFile.type },
        body: avatarFile
      });

      const updateResponse = await fetch(`${API_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ avatar_url: urlData.public_url })
      });
      if (!updateResponse.ok) {
        const err = await updateResponse.json();
        throw new Error(err.detail || 'Failed to save avatar');
      }
      setProfile(prev => ({ ...prev, avatar_url: urlData.public_url }));
      setMessage({ type: 'success', text: 'Avatar updated' });
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setSaving(false);
    }
  };

  const removeAvatar = async () => {
    try {
      setSaving(true);
      setMessage(null);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ avatar_url: null })
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to remove avatar');
      }
      setProfile(prev => ({ ...prev, avatar_url: '' }));
      setAvatarPreview('');
      setAvatarFile(null);
      setMessage({ type: 'success', text: 'Avatar removed' });
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setSaving(false);
    }
  };

  const handleConsentChange = (field, value) => {
    setConsent(prev => ({ ...prev, [field]: value }));
  };

  const saveProfile = async () => {
    try {
      setSaving(true);
      setMessage(null);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profile)
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Profile saved successfully' });
        if (onProfileUpdate) {
          onProfileUpdate({ ...user, name: profile.display_name });
        }
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to save profile' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save profile' });
    } finally {
      setSaving(false);
    }
  };

  const saveConsent = async () => {
    try {
      setSaving(true);
      setMessage(null);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_URL}/api/profile/consent`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(consent)
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Cookie preferences saved' });
      } else {
        setMessage({ type: 'error', text: 'Failed to save preferences' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save preferences' });
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: 'user' },
    { id: 'address', label: 'Address', icon: 'map' },
    { id: 'security', label: 'Security', icon: 'shield' },
    { id: 'cookies', label: 'Cookie Preferences', icon: 'cookie' }
  ];

  return (
    <div className="settings-page">
      {/* Header */}
      <div className="settings-header">
        <button className="settings-back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Back
        </button>
        <h1 className="settings-title">Settings</h1>
      </div>

      {/* Message */}
      {message && (
        <div className={`settings-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="settings-layout">
        {/* Tabs Navigation */}
        <div className="settings-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="settings-content">
          {loading ? (
            <div className="settings-loading">Loading...</div>
          ) : (
            <>
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="settings-section">
                  <h2 className="section-title">Profile Information</h2>
                  <p className="section-description">
                    Update your personal information and how others see you on LEGID.
                  </p>

                  <div className="avatar-section">
                    <div className="avatar-preview">
                      {avatarPreview ? (
                        <img src={avatarPreview} alt="Avatar preview" />
                      ) : (
                        <div className="avatar-placeholder">
                          {(profile.display_name || user?.email || 'U').charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="avatar-actions">
                      <input
                        type="file"
                        id="avatar-upload"
                        accept="image/png,image/jpeg,image/webp,image/jpg"
                        onChange={handleAvatarChange}
                        hidden
                      />
                      <label htmlFor="avatar-upload" className="secondary-btn">
                        Upload
                      </label>
                      <button className="secondary-btn" onClick={uploadAvatar} disabled={!avatarFile || saving}>
                        Save
                      </button>
                      <button className="secondary-btn" onClick={removeAvatar} disabled={saving}>
                        Remove
                      </button>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Display Name</label>
                    <input
                      type="text"
                      value={profile.display_name}
                      onChange={(e) => handleProfileChange('display_name', e.target.value)}
                      placeholder="Your display name"
                    />
                  </div>

                  <div className="form-group">
                    <label>Username</label>
                    <input
                      type="text"
                      value={profile.username}
                      onChange={(e) => handleProfileChange('username', e.target.value)}
                      placeholder="@username"
                    />
                    <span className="form-hint">This will be your unique identifier</span>
                  </div>

                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      value={profile.phone}
                      onChange={(e) => handleProfileChange('phone', e.target.value)}
                      placeholder="+1 (555) 000-0000"
                    />
                  </div>

                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="disabled"
                    />
                    <span className="form-hint">Email cannot be changed</span>
                  </div>

                  <button 
                    className="save-btn" 
                    onClick={saveProfile}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}

              {/* Address Tab */}
              {activeTab === 'address' && (
                <div className="settings-section">
                  <h2 className="section-title">Address</h2>
                  <p className="section-description">
                    Your address is used for legal document generation and jurisdiction detection.
                  </p>

                  <div className="form-group">
                    <label>Address Line 1</label>
                    <input
                      type="text"
                      value={profile.address_line_1}
                      onChange={(e) => handleProfileChange('address_line_1', e.target.value)}
                      placeholder="Street address"
                    />
                  </div>

                  <div className="form-group">
                    <label>Address Line 2</label>
                    <input
                      type="text"
                      value={profile.address_line_2}
                      onChange={(e) => handleProfileChange('address_line_2', e.target.value)}
                      placeholder="Apartment, suite, etc. (optional)"
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>City</label>
                      <input
                        type="text"
                        value={profile.city}
                        onChange={(e) => handleProfileChange('city', e.target.value)}
                        placeholder="City"
                      />
                    </div>

                    <div className="form-group">
                      <label>Province/State</label>
                      <input
                        type="text"
                        value={profile.province_state}
                        onChange={(e) => handleProfileChange('province_state', e.target.value)}
                        placeholder="Province or State"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Postal/ZIP Code</label>
                      <input
                        type="text"
                        value={profile.postal_zip}
                        onChange={(e) => handleProfileChange('postal_zip', e.target.value)}
                        placeholder="Postal or ZIP code"
                      />
                    </div>

                    <div className="form-group">
                      <label>Country</label>
                      <select
                        value={profile.country}
                        onChange={(e) => handleProfileChange('country', e.target.value)}
                      >
                        <option value="">Select Country</option>
                        <option value="Canada">Canada</option>
                        <option value="United States">United States</option>
                      </select>
                    </div>
                  </div>

                  <button 
                    className="save-btn" 
                    onClick={saveProfile}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Address'}
                  </button>
                </div>
              )}

              {/* Security Tab */}
              {activeTab === 'security' && (
                <div className="settings-section">
                  <h2 className="section-title">Security</h2>
                  <p className="section-description">
                    Manage your account security and authentication settings.
                  </p>

                  <div className="security-item">
                    <div className="security-info">
                      <h3>Connected Accounts</h3>
                      <p>Manage your connected OAuth accounts</p>
                    </div>
                    <div className="connected-accounts">
                      {user?.auth_provider === 'google' && (
                        <div className="connected-account">
                          <svg viewBox="0 0 24 24" width="20" height="20">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                          </svg>
                          <span>Google Connected</span>
                        </div>
                      )}
                      {user?.auth_provider === 'microsoft' && (
                        <div className="connected-account">
                          <svg viewBox="0 0 24 24" width="20" height="20">
                            <path fill="#F25022" d="M1 1h10v10H1z"/>
                            <path fill="#7FBA00" d="M13 1h10v10H13z"/>
                            <path fill="#00A4EF" d="M1 13h10v10H1z"/>
                            <path fill="#FFB900" d="M13 13h10v10H13z"/>
                          </svg>
                          <span>Microsoft Connected</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="security-item">
                    <div className="security-info">
                      <h3>Active Sessions</h3>
                      <p>View and manage your active login sessions</p>
                    </div>
                    <button className="secondary-btn">View Sessions</button>
                  </div>

                  <div className="security-item">
                    <div className="security-info">
                      <h3>Two-Factor Authentication</h3>
                      <p>Add an extra layer of security to your account</p>
                    </div>
                    <button className="secondary-btn">Set Up 2FA</button>
                  </div>
                </div>
              )}

              {/* Cookies Tab */}
              {activeTab === 'cookies' && (
                <div className="settings-section">
                  <h2 className="section-title">Cookie Preferences</h2>
                  <p className="section-description">
                    Manage how we use cookies to personalize your experience.
                  </p>

                  <div className="cookie-item">
                    <div className="cookie-info">
                      <h3>Necessary Cookies</h3>
                      <p>Required for the website to function. Cannot be disabled.</p>
                    </div>
                    <div className="toggle disabled">
                      <input type="checkbox" checked disabled />
                      <span className="toggle-slider"></span>
                    </div>
                  </div>

                  <div className="cookie-item">
                    <div className="cookie-info">
                      <h3>Functional Cookies</h3>
                      <p>Remember your preferences and settings.</p>
                    </div>
                    <div className="toggle">
                      <input 
                        type="checkbox" 
                        checked={consent.functional}
                        onChange={(e) => handleConsentChange('functional', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </div>
                  </div>

                  <div className="cookie-item">
                    <div className="cookie-info">
                      <h3>Analytics Cookies</h3>
                      <p>Help us understand how you use our service.</p>
                    </div>
                    <div className="toggle">
                      <input 
                        type="checkbox" 
                        checked={consent.analytics}
                        onChange={(e) => handleConsentChange('analytics', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </div>
                  </div>

                  <div className="cookie-item">
                    <div className="cookie-info">
                      <h3>Marketing Cookies</h3>
                      <p>Used to show you relevant content and offers.</p>
                    </div>
                    <div className="toggle">
                      <input 
                        type="checkbox" 
                        checked={consent.marketing}
                        onChange={(e) => handleConsentChange('marketing', e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </div>
                  </div>

                  <button 
                    className="save-btn" 
                    onClick={saveConsent}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
