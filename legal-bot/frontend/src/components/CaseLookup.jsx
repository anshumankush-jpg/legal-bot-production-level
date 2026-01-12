import React, { useState } from 'react';
import './CaseLookup.css';

const CaseLookup = ({ onClose, onCaseSelected }) => {
  const [query, setQuery] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [yearFrom, setYearFrom] = useState('');
  const [yearTo, setYearTo] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/api/legal/case-lookup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          jurisdiction: jurisdiction || null,
          year_from: yearFrom ? parseInt(yearFrom) : null,
          year_to: yearTo ? parseInt(yearTo) : null,
          limit: 10
        })
      });

      const data = await response.json();

      if (data.success) {
        setResults(data);
      } else {
        setError(data.error || 'Failed to search cases');
        if (data.upgrade_info) {
          setError(`${data.error}. ${data.upgrade_info.message}`);
        }
      }
    } catch (err) {
      setError('Failed to connect to the server');
      console.error('Case lookup error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCaseClick = (caseItem) => {
    if (onCaseSelected) {
      onCaseSelected(caseItem);
    }
  };

  return (
    <div className="case-lookup-overlay">
      <div className="case-lookup-modal">
        <div className="case-lookup-header">
          <h2>🔍 Case Lookup</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="case-lookup-content">
          <div className="search-form">
            <div className="form-group">
              <label>Search Query</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Case name, citation, or keywords..."
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Jurisdiction (Optional)</label>
                <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
                  <option value="">All Jurisdictions</option>
                  <option value="US">United States</option>
                  <option value="CA">Canada</option>
                  <option value="US-NY">New York</option>
                  <option value="US-CA">California</option>
                  <option value="US-TX">Texas</option>
                  <option value="CA-ON">Ontario</option>
                  <option value="CA-QC">Quebec</option>
                  <option value="CA-BC">British Columbia</option>
                </select>
              </div>

              <div className="form-group">
                <label>Year From</label>
                <input
                  type="number"
                  value={yearFrom}
                  onChange={(e) => setYearFrom(e.target.value)}
                  placeholder="e.g., 2000"
                  min="1800"
                  max={new Date().getFullYear()}
                />
              </div>

              <div className="form-group">
                <label>Year To</label>
                <input
                  type="number"
                  value={yearTo}
                  onChange={(e) => setYearTo(e.target.value)}
                  placeholder="e.g., 2024"
                  min="1800"
                  max={new Date().getFullYear()}
                />
              </div>
            </div>

            <button 
              className="search-button" 
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search Cases'}
            </button>
          </div>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {results && (
            <div className="search-results">
              <div className="results-header">
                <h3>Search Results</h3>
                <span className="results-count">
                  {results.total} case{results.total !== 1 ? 's' : ''} found
                </span>
                {results.note && (
                  <div className="results-note">ℹ️ {results.note}</div>
                )}
              </div>

              <div className="results-list">
                {results.results && results.results.map((caseItem, index) => (
                  <div 
                    key={index} 
                    className="case-item"
                    onClick={() => handleCaseClick(caseItem)}
                  >
                    <div className="case-header">
                      <h4>{caseItem.case_name}</h4>
                      <span className="case-citation">{caseItem.citation}</span>
                    </div>
                    <div className="case-meta">
                      <span className="case-court">{caseItem.court}</span>
                      <span className="case-year">{caseItem.year}</span>
                      <span className="case-jurisdiction">{caseItem.jurisdiction}</span>
                      {caseItem.relevance_score && (
                        <span className="case-relevance">
                          Relevance: {(caseItem.relevance_score * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    <p className="case-summary">{caseItem.summary}</p>
                    {caseItem.url && (
                      <a 
                        href={caseItem.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="case-link"
                        onClick={(e) => e.stopPropagation()}
                      >
                        View Full Case →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseLookup;
