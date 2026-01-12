import React, { useState, useEffect } from 'react';
import './RecentUpdates.css';

const RecentUpdates = ({ lawType, jurisdiction, onClose }) => {
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentUpdates();
  }, [lawType, jurisdiction]);

  const fetchRecentUpdates = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/artillery/recent-updates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          law_type: lawType,
          jurisdiction: jurisdiction
        })
      });

      if (response.ok) {
        const data = await response.json();
        setUpdates(data.updates || []);
      }
    } catch (error) {
      console.error('Error fetching updates:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <div className="recent-updates-modal">
      <div className="updates-container">
        <div className="updates-header">
          <h2>Recent Updates: {lawType}</h2>
          <p className="jurisdiction-label">{jurisdiction}</p>
          <button className="close-btn" onClick={onClose}>Close</button>
        </div>

        {loading ? (
          <div className="updates-loading">
            <div className="loading-spinner"></div>
            <p>Fetching recent legal updates...</p>
          </div>
        ) : (
          <div className="updates-list">
            {updates.length === 0 ? (
              <div className="no-updates">
                <p>No recent updates available for this law type and jurisdiction.</p>
                <p className="note">Updates are refreshed daily at 2:00 AM</p>
              </div>
            ) : (
              updates.map((update, index) => (
                <div key={index} className="update-card">
                  <div className="update-header">
                    <span className="update-type">{update.type}</span>
                    <span className="update-date">{formatDate(update.date)}</span>
                  </div>
                  
                  <h3 className="update-title">{update.title}</h3>
                  
                  <p className="update-summary">{update.summary}</p>
                  
                  {update.citation && (
                    <div className="update-citation">
                      <strong>Citation:</strong> {update.citation}
                    </div>
                  )}
                  
                  {update.key_changes && update.key_changes.length > 0 && (
                    <div className="update-changes">
                      <strong>Key Changes:</strong>
                      <ul>
                        {update.key_changes.map((change, idx) => (
                          <li key={idx}>{change}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {update.effective_date && (
                    <div className="update-effective">
                      <strong>Effective Date:</strong> {formatDate(update.effective_date)}
                    </div>
                  )}
                  
                  {update.source_url && (
                    <div className="update-source">
                      <a 
                        href={update.source_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        View Official Source
                      </a>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        <div className="updates-footer">
          <p>Data sourced from official government and legal databases</p>
          <p>Updates are automatically fetched and verified daily</p>
        </div>
      </div>
    </div>
  );
};

export default RecentUpdates;
