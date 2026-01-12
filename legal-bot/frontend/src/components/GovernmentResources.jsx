import React from 'react';
import './GovernmentResources.css';

const GovernmentResources = ({ resources, lawType, province }) => {
  if (!resources || resources.length === 0) {
    return null;
  }

  // Province name mapping
  const provinceNames = {
    'ON': 'Ontario',
    'QC': 'Quebec',
    'BC': 'British Columbia',
    'AB': 'Alberta',
    'MB': 'Manitoba',
    'SK': 'Saskatchewan',
    'NS': 'Nova Scotia',
    'NB': 'New Brunswick',
    'PE': 'Prince Edward Island',
    'NL': 'Newfoundland and Labrador',
    'YT': 'Yukon',
    'NT': 'Northwest Territories',
    'NU': 'Nunavut'
  };

  const provinceName = province ? provinceNames[province] || province : 'Canada';

  return (
    <div className="government-resources">
      <h3 className="resources-title">
        📑 Official Government Resources for {lawType}
        {province && <span className="province-badge">{provinceName}</span>}
      </h3>
      <div className="resources-grid">
        {resources.map((resource, idx) => (
          <a 
            key={idx}
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="resource-card"
          >
            <div className="resource-header">
              <span className="resource-icon">🔗</span>
              <span className="resource-number">#{idx + 1}</span>
            </div>
            <h4 className="resource-title">{resource.title}</h4>
            <p className="resource-source">
              <span className="source-label">Source:</span> {resource.source}
            </p>
            <div className="resource-url">
              <span className="url-icon">🌐</span>
              <span className="url-text">{new URL(resource.url).hostname}</span>
            </div>
            <div className="resource-hover-text">
              Click to visit →
            </div>
          </a>
        ))}
      </div>
      <p className="resources-note">
        ℹ️ These are official government websites with up-to-date legal information and resources for {provinceName}.
      </p>
    </div>
  );
};

export default GovernmentResources;
