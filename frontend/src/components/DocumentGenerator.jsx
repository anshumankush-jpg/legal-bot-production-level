import React, { useState } from 'react';
import './DocumentGenerator.css';
import jsPDF from 'jspdf';

const DocumentGenerator = ({ onClose, lawCategory, userId = 'default_user' }) => {
  const [step, setStep] = useState(1); // Multi-step wizard
  const [documentType, setDocumentType] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [formData, setFormData] = useState({});
  const [generatedDocument, setGeneratedDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [previewMode, setPreviewMode] = useState(false);

  // Document types available
  const documentTypes = {
    'sue_letter': {
      name: 'Sue Letter (Legal Complaint)',
      icon: '⚖️',
      description: 'File a legal complaint against a defendant',
      fields: [
        { name: 'defendant_name', label: 'Defendant Name', type: 'text', required: true },
        { name: 'defendant_address', label: 'Defendant Address', type: 'textarea', required: true },
        { name: 'plaintiff_name', label: 'Your Name (Plaintiff)', type: 'text', required: true },
        { name: 'plaintiff_address', label: 'Your Address', type: 'textarea', required: true },
        { name: 'legal_grounds', label: 'Legal Grounds for Lawsuit', type: 'textarea', required: true, placeholder: 'Describe the reason for the lawsuit (e.g., breach of contract, negligence)' },
        { name: 'relief_sought', label: 'Relief Sought', type: 'textarea', required: true, placeholder: 'What compensation or remedy are you seeking?' },
        { name: 'incident_date', label: 'Date of Incident', type: 'date', required: false },
        { name: 'damages_amount', label: 'Damages Amount ($)', type: 'number', required: false },
        { name: 'additional_clauses', label: 'Additional Clauses', type: 'textarea', required: false }
      ]
    },
    'amendment': {
      name: 'Amendment to Contract',
      icon: '📝',
      description: 'Modify terms of an existing contract',
      fields: [
        { name: 'original_contract_name', label: 'Original Contract Name/Reference', type: 'text', required: true },
        { name: 'party_a', label: 'Party A Name', type: 'text', required: true },
        { name: 'party_b', label: 'Party B Name', type: 'text', required: true },
        { name: 'sections_to_amend', label: 'Sections to Amend', type: 'textarea', required: true, placeholder: 'List the sections/clauses to be amended (e.g., Section 5, Clause 10)' },
        { name: 'reason_for_amendment', label: 'Reason for Amendment', type: 'textarea', required: true },
        { name: 'new_terms', label: 'New Terms/Conditions', type: 'textarea', required: true, placeholder: 'Describe the new terms that will replace the old ones' },
        { name: 'effective_date', label: 'Effective Date', type: 'date', required: true },
        { name: 'additional_notes', label: 'Additional Notes', type: 'textarea', required: false }
      ]
    },
    'nda': {
      name: 'Non-Disclosure Agreement (NDA)',
      icon: '🤐',
      description: 'Protect confidential information',
      fields: [
        { name: 'disclosing_party', label: 'Disclosing Party Name', type: 'text', required: true },
        { name: 'receiving_party', label: 'Receiving Party Name', type: 'text', required: true },
        { name: 'purpose', label: 'Purpose of Disclosure', type: 'textarea', required: true },
        { name: 'confidential_info', label: 'Description of Confidential Information', type: 'textarea', required: true },
        { name: 'term_years', label: 'Term (Years)', type: 'number', required: true, placeholder: '2' },
        { name: 'effective_date', label: 'Effective Date', type: 'date', required: true },
        { name: 'governing_law', label: 'Governing Law', type: 'text', required: false }
      ]
    },
    'will': {
      name: 'Last Will and Testament',
      icon: '📜',
      description: 'Estate planning document',
      fields: [
        { name: 'testator_name', label: 'Your Full Name', type: 'text', required: true },
        { name: 'testator_address', label: 'Your Address', type: 'textarea', required: true },
        { name: 'executor_name', label: 'Executor Name', type: 'text', required: true },
        { name: 'executor_address', label: 'Executor Address', type: 'textarea', required: true },
        { name: 'beneficiaries', label: 'Beneficiaries', type: 'textarea', required: true, placeholder: 'List all beneficiaries and their shares' },
        { name: 'specific_bequests', label: 'Specific Bequests', type: 'textarea', required: false, placeholder: 'Any specific items to be given to specific people' },
        { name: 'guardian_minor', label: 'Guardian for Minor Children', type: 'text', required: false }
      ]
    },
    'power_of_attorney': {
      name: 'Power of Attorney',
      icon: '✍️',
      description: 'Authorize someone to act on your behalf',
      fields: [
        { name: 'principal_name', label: 'Principal Name (You)', type: 'text', required: true },
        { name: 'principal_address', label: 'Principal Address', type: 'textarea', required: true },
        { name: 'agent_name', label: 'Agent Name (Attorney-in-Fact)', type: 'text', required: true },
        { name: 'agent_address', label: 'Agent Address', type: 'textarea', required: true },
        { name: 'powers_granted', label: 'Powers Granted', type: 'textarea', required: true, placeholder: 'Describe what powers you are granting' },
        { name: 'effective_date', label: 'Effective Date', type: 'date', required: true },
        { name: 'durable', label: 'Durable (Survives Incapacity)', type: 'checkbox', required: false }
      ]
    },
    'lease_agreement': {
      name: 'Lease Agreement',
      icon: '🏠',
      description: 'Rental property agreement',
      fields: [
        { name: 'landlord_name', label: 'Landlord Name', type: 'text', required: true },
        { name: 'tenant_name', label: 'Tenant Name', type: 'text', required: true },
        { name: 'property_address', label: 'Property Address', type: 'textarea', required: true },
        { name: 'lease_term', label: 'Lease Term (Months)', type: 'number', required: true },
        { name: 'monthly_rent', label: 'Monthly Rent ($)', type: 'number', required: true },
        { name: 'security_deposit', label: 'Security Deposit ($)', type: 'number', required: true },
        { name: 'start_date', label: 'Lease Start Date', type: 'date', required: true },
        { name: 'utilities_included', label: 'Utilities Included', type: 'textarea', required: false },
        { name: 'pet_policy', label: 'Pet Policy', type: 'textarea', required: false }
      ]
    },
    'employment_contract': {
      name: 'Employment Contract',
      icon: '💼',
      description: 'Employment agreement',
      fields: [
        { name: 'employer_name', label: 'Employer Name', type: 'text', required: true },
        { name: 'employee_name', label: 'Employee Name', type: 'text', required: true },
        { name: 'position', label: 'Job Position', type: 'text', required: true },
        { name: 'start_date', label: 'Start Date', type: 'date', required: true },
        { name: 'salary', label: 'Annual Salary ($)', type: 'number', required: true },
        { name: 'benefits', label: 'Benefits', type: 'textarea', required: false },
        { name: 'work_hours', label: 'Work Hours', type: 'text', required: false, placeholder: 'e.g., 9 AM - 5 PM, Monday-Friday' },
        { name: 'probation_period', label: 'Probation Period (Days)', type: 'number', required: false },
        { name: 'termination_notice', label: 'Termination Notice (Days)', type: 'number', required: false }
      ]
    },
    'business_contract': {
      name: 'Business Contract',
      icon: '🤝',
      description: 'General business agreement',
      fields: [
        { name: 'party_a_name', label: 'Party A Name', type: 'text', required: true },
        { name: 'party_b_name', label: 'Party B Name', type: 'text', required: true },
        { name: 'contract_purpose', label: 'Purpose of Contract', type: 'textarea', required: true },
        { name: 'obligations_party_a', label: 'Obligations of Party A', type: 'textarea', required: true },
        { name: 'obligations_party_b', label: 'Obligations of Party B', type: 'textarea', required: true },
        { name: 'payment_terms', label: 'Payment Terms', type: 'textarea', required: true },
        { name: 'contract_term', label: 'Contract Term', type: 'text', required: true, placeholder: 'e.g., 12 months, 2 years' },
        { name: 'effective_date', label: 'Effective Date', type: 'date', required: true }
      ]
    }
  };

  const handleDocumentTypeSelect = (type) => {
    setDocumentType(type);
    setFormData({});
    setStep(2);
  };

  const handleInputChange = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const validateForm = () => {
    const docType = documentTypes[documentType];
    if (!docType) return false;

    for (const field of docType.fields) {
      if (field.required && !formData[field.name]) {
        setError(`Please fill in: ${field.label}`);
        return false;
      }
    }
    return true;
  };

  const handleGenerate = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/legal/generate-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_type: documentType,
          jurisdiction: jurisdiction || 'US',
          form_data: formData,
          user_id: userId
        })
      });

      const data = await response.json();

      if (data.success) {
        setGeneratedDocument(data);
        setPreviewMode(true);
        setStep(3);
      } else {
        setError(data.error || 'Failed to generate document');
      }
    } catch (err) {
      setError('Failed to connect to the server');
      console.error('Document generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!generatedDocument || !generatedDocument.content) return;

    try {
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      const maxWidth = pageWidth - 2 * margin;
      
      // Title
      doc.setFontSize(16);
      doc.setFont(undefined, 'bold');
      doc.text(documentTypes[documentType].name, margin, margin);
      
      // Content
      doc.setFontSize(11);
      doc.setFont(undefined, 'normal');
      
      const lines = doc.splitTextToSize(generatedDocument.content, maxWidth);
      let y = margin + 10;
      
      lines.forEach(line => {
        if (y > pageHeight - margin) {
          doc.addPage();
          y = margin;
        }
        doc.text(line, margin, y);
        y += 7;
      });
      
      // Footer
      const totalPages = doc.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        doc.setFontSize(9);
        doc.text(
          `Page ${i} of ${totalPages} - Generated: ${new Date().toLocaleDateString()}`,
          pageWidth / 2,
          pageHeight - 10,
          { align: 'center' }
        );
      }
      
      doc.save(`${documentType}_${Date.now()}.pdf`);
    } catch (err) {
      console.error('PDF generation error:', err);
      alert('Failed to generate PDF. Downloading as text file instead.');
      handleDownloadText();
    }
  };

  const handleDownloadText = () => {
    if (!generatedDocument || !generatedDocument.content) return;

    const blob = new Blob([generatedDocument.content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${documentType}_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleCopy = () => {
    if (!generatedDocument || !generatedDocument.content) return;

    navigator.clipboard.writeText(generatedDocument.content).then(() => {
      alert('Document copied to clipboard!');
    });
  };

  const handleEdit = () => {
    setPreviewMode(false);
    setStep(2);
  };

  const renderStep1 = () => (
    <div className="document-type-selection">
      <h3>Select Document Type</h3>
      <div className="document-types-grid">
        {Object.entries(documentTypes).map(([key, doc]) => (
          <div
            key={key}
            className="document-type-card"
            onClick={() => handleDocumentTypeSelect(key)}
          >
            <div className="doc-icon">{doc.icon}</div>
            <h4>{doc.name}</h4>
            <p>{doc.description}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep2 = () => {
    const docType = documentTypes[documentType];
    if (!docType) return null;

    return (
      <div className="document-form">
        <div className="form-header">
          <h3>{docType.icon} {docType.name}</h3>
          <p>{docType.description}</p>
        </div>

        <div className="form-group">
          <label>Jurisdiction (Optional)</label>
          <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}>
            <option value="">Select jurisdiction...</option>
            <optgroup label="🇺🇸 United States">
              <option value="US">United States (Federal)</option>
              <option value="US-CA">California</option>
              <option value="US-NY">New York</option>
              <option value="US-TX">Texas</option>
              <option value="US-FL">Florida</option>
            </optgroup>
            <optgroup label="🇨🇦 Canada">
              <option value="CA">Canada (Federal)</option>
              <option value="CA-ON">Ontario</option>
              <option value="CA-QC">Quebec</option>
              <option value="CA-BC">British Columbia</option>
            </optgroup>
          </select>
        </div>

        {docType.fields.map((field) => (
          <div key={field.name} className="form-group">
            <label>
              {field.label} {field.required && <span className="required">*</span>}
            </label>
            {field.type === 'textarea' ? (
              <textarea
                value={formData[field.name] || ''}
                onChange={(e) => handleInputChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                rows={4}
              />
            ) : field.type === 'checkbox' ? (
              <input
                type="checkbox"
                checked={formData[field.name] || false}
                onChange={(e) => handleInputChange(field.name, e.target.checked)}
              />
            ) : (
              <input
                type={field.type}
                value={formData[field.name] || ''}
                onChange={(e) => handleInputChange(field.name, e.target.value)}
                placeholder={field.placeholder}
              />
            )}
          </div>
        ))}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="form-actions">
          <button className="btn-secondary" onClick={() => setStep(1)}>
            ← Back
          </button>
          <button 
            className="btn-primary" 
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Document'}
          </button>
        </div>

        <div className="disclaimer">
          ⚠️ <strong>Disclaimer:</strong> This is an automated document generator. 
          Always have legal documents reviewed by a licensed attorney before use.
        </div>
      </div>
    );
  };

  const renderStep3 = () => {
    if (!generatedDocument) return null;

    return (
      <div className="document-preview">
        <div className="preview-header">
          <h3>✅ Document Generated</h3>
          <div className="preview-actions">
            <button className="btn-action" onClick={handleEdit}>
              ✏️ Edit
            </button>
            <button className="btn-action" onClick={handleCopy}>
              📋 Copy
            </button>
            <button className="btn-action" onClick={handleDownloadText}>
              💾 Download TXT
            </button>
            <button className="btn-action" onClick={handleDownloadPDF}>
              📄 Download PDF
            </button>
          </div>
        </div>

        {generatedDocument.note && (
          <div className="preview-note">
            ℹ️ {generatedDocument.note}
          </div>
        )}

        <div className="preview-content">
          <pre>{generatedDocument.content}</pre>
        </div>

        <div className="preview-meta">
          <span>Document ID: {generatedDocument.document_id}</span>
          <span>Source: {generatedDocument.source}</span>
          <span>Generated: {new Date().toLocaleString()}</span>
        </div>

        <div className="preview-footer">
          <button className="btn-secondary" onClick={() => {
            setStep(1);
            setGeneratedDocument(null);
            setFormData({});
            setDocumentType('');
          }}>
            Generate New Document
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="document-generator-overlay">
      <div className="document-generator-modal">
        <div className="modal-header">
          <h2>📄 Legal Document Generator</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="progress-indicator">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">Select Type</span>
          </div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">Fill Details</span>
          </div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">Preview & Download</span>
          </div>
        </div>

        <div className="modal-content">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>
      </div>
    </div>
  );
};

export default DocumentGenerator;
