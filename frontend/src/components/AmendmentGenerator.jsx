import React, { useState } from 'react';
import './AmendmentGenerator.css';

const AmendmentGenerator = ({ onClose, lawCategory }) => {
  const [documentType, setDocumentType] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [caseDetails, setCaseDetails] = useState({
    amendment_text: '',
    party_a: '',
    party_b: '',
    effective_date: '',
    additional_notes: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const documentTypes = {
    'Family Law': ['divorce', 'custody', 'prenuptial', 'separation'],
    'Business Litigation': ['contract', 'partnership', 'settlement', 'nda'],
    'Real Estate Law': ['lease', 'purchase', 'mortgage', 'easement'],
    'Wills, Estates, and Trusts': ['will', 'trust', 'power_of_attorney', 'estate'],
    'Employment Law': ['employment_contract', 'severance', 'non_compete'],
    'default': ['contract', 'agreement', 'amendment', 'addendum']
  };

  const getDocumentTypes = () => {
    return documentTypes[lawCategory] || documentTypes['default'];
  };

  const handleGenerate = async () => {
    if (!documentType) {
      setError('Please select a document type');
      return;
    }

    if (!caseDetails.amendment_text.trim()) {
      setError('Please provide amendment details');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/legal/generate-amendment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_type: documentType,
          case_details: caseDetails,
          jurisdiction: jurisdiction || null
        })
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to generate amendment');
        if (data.upgrade_info) {
          setError(`${data.error}. ${data.upgrade_info.message}`);
        }
      }
    } catch (err) {
      setError('Failed to connect to the server');
      console.error('Amendment generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result || !result.content) return;

    const blob = new Blob([result.content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `amendment_${documentType}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleCopy = () => {
    if (!result || !result.content) return;

    navigator.clipboard.writeText(result.content).then(() => {
      alert('Amendment copied to clipboard!');
    });
  };

  return (
    <div className="amendment-overlay">
      <div className="amendment-modal">
        <div className="amendment-header">
          <h2>📝 Amendment Generator</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="amendment-content">
          {!result ? (
            <div className="amendment-form">
              <div className="form-group">
                <label>Document Type *</label>
                <select 
                  value={documentType} 
                  onChange={(e) => setDocumentType(e.target.value)}
                >
                  <option value="">Select document type...</option>
                  {getDocumentTypes().map(type => (
                    <option key={type} value={type}>
                      {type.replace(/_/g, ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Jurisdiction (Optional)</label>
                <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
                  <option value="">Select jurisdiction...</option>
                  
                  <optgroup label="🇺🇸 United States">
                    <option value="US">United States (Federal)</option>
                    <option value="US-AL">Alabama</option>
                    <option value="US-AK">Alaska</option>
                    <option value="US-AZ">Arizona</option>
                    <option value="US-AR">Arkansas</option>
                    <option value="US-CA">California</option>
                    <option value="US-CO">Colorado</option>
                    <option value="US-CT">Connecticut</option>
                    <option value="US-DE">Delaware</option>
                    <option value="US-FL">Florida</option>
                    <option value="US-GA">Georgia</option>
                    <option value="US-HI">Hawaii</option>
                    <option value="US-ID">Idaho</option>
                    <option value="US-IL">Illinois</option>
                    <option value="US-IN">Indiana</option>
                    <option value="US-IA">Iowa</option>
                    <option value="US-KS">Kansas</option>
                    <option value="US-KY">Kentucky</option>
                    <option value="US-LA">Louisiana</option>
                    <option value="US-ME">Maine</option>
                    <option value="US-MD">Maryland</option>
                    <option value="US-MA">Massachusetts</option>
                    <option value="US-MI">Michigan</option>
                    <option value="US-MN">Minnesota</option>
                    <option value="US-MS">Mississippi</option>
                    <option value="US-MO">Missouri</option>
                    <option value="US-MT">Montana</option>
                    <option value="US-NE">Nebraska</option>
                    <option value="US-NV">Nevada</option>
                    <option value="US-NH">New Hampshire</option>
                    <option value="US-NJ">New Jersey</option>
                    <option value="US-NM">New Mexico</option>
                    <option value="US-NY">New York</option>
                    <option value="US-NC">North Carolina</option>
                    <option value="US-ND">North Dakota</option>
                    <option value="US-OH">Ohio</option>
                    <option value="US-OK">Oklahoma</option>
                    <option value="US-OR">Oregon</option>
                    <option value="US-PA">Pennsylvania</option>
                    <option value="US-RI">Rhode Island</option>
                    <option value="US-SC">South Carolina</option>
                    <option value="US-SD">South Dakota</option>
                    <option value="US-TN">Tennessee</option>
                    <option value="US-TX">Texas</option>
                    <option value="US-UT">Utah</option>
                    <option value="US-VT">Vermont</option>
                    <option value="US-VA">Virginia</option>
                    <option value="US-WA">Washington</option>
                    <option value="US-WV">West Virginia</option>
                    <option value="US-WI">Wisconsin</option>
                    <option value="US-WY">Wyoming</option>
                  </optgroup>
                  
                  <optgroup label="🇨🇦 Canada">
                    <option value="CA">Canada (Federal)</option>
                    <option value="CA-AB">Alberta</option>
                    <option value="CA-BC">British Columbia</option>
                    <option value="CA-MB">Manitoba</option>
                    <option value="CA-NB">New Brunswick</option>
                    <option value="CA-NL">Newfoundland and Labrador</option>
                    <option value="CA-NS">Nova Scotia</option>
                    <option value="CA-ON">Ontario</option>
                    <option value="CA-PE">Prince Edward Island</option>
                    <option value="CA-QC">Quebec</option>
                    <option value="CA-SK">Saskatchewan</option>
                    <option value="CA-NT">Northwest Territories</option>
                    <option value="CA-NU">Nunavut</option>
                    <option value="CA-YT">Yukon</option>
                  </optgroup>
                </select>
              </div>

              <div className="form-group">
                <label>Amendment Details *</label>
                <textarea
                  value={caseDetails.amendment_text}
                  onChange={(e) => setCaseDetails({...caseDetails, amendment_text: e.target.value})}
                  placeholder="Describe the amendments you want to make to the document..."
                  rows="5"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Party A (Optional)</label>
                  <input
                    type="text"
                    value={caseDetails.party_a}
                    onChange={(e) => setCaseDetails({...caseDetails, party_a: e.target.value})}
                    placeholder="First party name"
                  />
                </div>

                <div className="form-group">
                  <label>Party B (Optional)</label>
                  <input
                    type="text"
                    value={caseDetails.party_b}
                    onChange={(e) => setCaseDetails({...caseDetails, party_b: e.target.value})}
                    placeholder="Second party name"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Effective Date (Optional)</label>
                <input
                  type="date"
                  value={caseDetails.effective_date}
                  onChange={(e) => setCaseDetails({...caseDetails, effective_date: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Additional Notes (Optional)</label>
                <textarea
                  value={caseDetails.additional_notes}
                  onChange={(e) => setCaseDetails({...caseDetails, additional_notes: e.target.value})}
                  placeholder="Any additional information or special requirements..."
                  rows="3"
                />
              </div>

              {error && (
                <div className="error-message">
                  ⚠️ {error}
                </div>
              )}

              <button 
                className="generate-button" 
                onClick={handleGenerate}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Amendment'}
              </button>

              <div className="disclaimer">
                ⚠️ <strong>Disclaimer:</strong> This is an automated document generator. 
                Always have legal documents reviewed by a licensed attorney before use.
              </div>
            </div>
          ) : (
            <div className="amendment-result">
              <div className="result-header">
                <h3>✅ Amendment Generated</h3>
                <div className="result-actions">
                  <button className="action-button" onClick={handleCopy}>
                    📋 Copy
                  </button>
                  <button className="action-button" onClick={handleDownload}>
                    💾 Download
                  </button>
                  <button className="action-button" onClick={() => setResult(null)}>
                    🔄 Generate New
                  </button>
                </div>
              </div>

              {result.note && (
                <div className="result-note">
                  ℹ️ {result.note}
                </div>
              )}

              <div className="result-content">
                <pre>{result.content}</pre>
              </div>

              <div className="result-meta">
                <span>Document ID: {result.document_id}</span>
                <span>Source: {result.source}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AmendmentGenerator;
