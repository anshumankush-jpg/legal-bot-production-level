import React, { useState } from 'react';
import './LawTypeSelector.css';

const LawTypeSelector = ({ preferences, onComplete, onBack, userRole }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedLawType, setSelectedLawType] = useState(null);

  // Comprehensive law categories - Canada & USA with Scopes
  const lawCategories = {
    'Constitutional Law': {
      description: 'Highest law of the country, protects fundamental rights and freedoms',
      scope: 'STRICT SCOPE: Only answer questions about constitutional rights, Charter of Rights and Freedoms (Canada), Bill of Rights (USA), constitutional challenges, Supreme Court constitutional decisions, and fundamental freedoms (speech, religion, equality, due process). REFUSE questions about other law areas.',
      jurisdictions: ['Federal']
    },
    'Criminal Law': {
      description: 'Crimes against society prosecuted by government',
      scope: 'STRICT SCOPE: Only answer questions about criminal offenses, criminal charges, penalties, criminal court procedures, criminal defenses, arrests, criminal trials, bail, sentencing. Examples: theft, assault, murder, fraud, drug offenses, sexual offenses, impaired driving, DUI. REFUSE questions about civil matters or non-criminal topics.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Civil Law': {
      description: 'Disputes between people or organizations',
      scope: 'STRICT SCOPE: Only answer questions about civil disputes, civil lawsuits, contracts, personal injury claims, property disputes, negligence, torts, damages, civil litigation procedures, settlements. REFUSE questions about criminal law or other topics.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Administrative Law': {
      description: 'Government agencies and administrative tribunals',
      scope: 'STRICT SCOPE: Only answer questions about government agency decisions, administrative tribunals, regulatory boards, immigration rulings (IRB), tax appeals, employment insurance tribunals, licensing boards, regulatory compliance, judicial review of government decisions. REFUSE non-administrative questions.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Family Law': {
      description: 'Marriage, divorce, children, and family relationships',
      scope: 'STRICT SCOPE: Only answer questions about marriage, divorce, separation, child custody, child support, spousal support, adoption, family property division, prenuptial agreements, cohabitation agreements, matrimonial home. REFUSE questions not related to family matters.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Traffic Law': {
      description: 'Traffic violations and highway offenses',
      scope: 'STRICT SCOPE: Only answer questions about traffic tickets, speeding, red-light violations, careless driving, stunt driving, distracted driving, driving without insurance, license suspensions, demerit points, provincial highway traffic offenses, parking violations. REFUSE questions about criminal driving (DUI is criminal law).',
      jurisdictions: ['Provincial']
    },
    'Business Litigation': {
      description: 'Business disputes and commercial litigation',
      scope: 'STRICT SCOPE: Only answer questions about business lawsuits, commercial disputes, breach of contract, partnership disputes, shareholder conflicts, corporate governance litigation, franchise disputes, intellectual property litigation, business torts, commercial arbitration. REFUSE non-litigation business questions.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Business Law': {
      description: 'Formation, operation, and transactions of businesses',
      scope: 'STRICT SCOPE: Only answer questions about business formation, incorporation, business contracts, mergers and acquisitions, corporate compliance, business financing, franchising, intellectual property (non-litigation), commercial transactions, business operations. REFUSE business litigation questions.',
      jurisdictions: ['Federal', 'Provincial', 'Municipal']
    },
    'Employment Law': {
      description: 'Workplace rights and employer-employee relations',
      scope: 'STRICT SCOPE: Only answer questions about employment contracts, wrongful dismissal, workplace harassment, workplace discrimination, employee rights, employer obligations, labor standards, workplace safety, human rights in employment, severance pay. REFUSE non-employment questions.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Real Estate Law': {
      description: 'Property ownership and real estate transactions',
      scope: 'STRICT SCOPE: Only answer questions about buying/selling property, real estate contracts, landlord-tenant law, property disputes, mortgages, real estate closings, title issues, zoning, property rights, easements, condo law. REFUSE non-property questions.',
      jurisdictions: ['Provincial', 'Municipal']
    },
    'Immigration Law': {
      description: 'Immigration, citizenship, and refugee matters',
      scope: 'STRICT SCOPE: Only answer questions about immigration applications, visas, work permits, study permits, permanent residence, citizenship, refugee claims, deportation, immigration appeals (IRB), sponsorship, express entry, provincial nominee programs. REFUSE non-immigration questions.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Tax Law': {
      description: 'Federal and provincial taxation',
      scope: 'STRICT SCOPE: Only answer questions about income tax, corporate tax, sales tax (GST/HST), tax planning, tax audits, tax appeals, tax compliance, tax disputes with CRA or IRS, tax evasion penalties. REFUSE non-tax questions.',
      jurisdictions: ['Federal', 'Provincial']
    },
    'Wills, Estates, and Trusts': {
      description: 'Estate planning and probate',
      scope: 'STRICT SCOPE: Only answer questions about wills, estate planning, trusts, probate, estate administration, powers of attorney, guardianship, estate litigation, estate disputes, beneficiary rights, intestacy. REFUSE non-estate questions.',
      jurisdictions: ['Provincial']
    },
    'Health Law': {
      description: 'Healthcare and medical legal matters',
      scope: 'STRICT SCOPE: Only answer questions about medical malpractice, healthcare compliance, patient rights, mental health law, consent to treatment, long-term care regulations, healthcare contracts, medical licensing. REFUSE non-healthcare questions.',
      jurisdictions: ['Federal', 'Provincial']
    }
  };

  // Get applicable jurisdictions based on user's country and province
  const getApplicableJurisdictions = (category) => {
    if (!preferences) return lawCategories[category].jurisdictions;

    const jurisdictions = [];
    
    // Federal level
    if (lawCategories[category].jurisdictions.includes('Federal')) {
      jurisdictions.push({
        id: 'federal',
        name: preferences.country === 'CA' ? 'Federal (Canada)' : 'Federal (USA)',
        scope: 'federal'
      });
    }

    // Provincial/State level
    if (lawCategories[category].jurisdictions.includes('Provincial') && preferences.province) {
      jurisdictions.push({
        id: `provincial_${preferences.province}`,
        name: `${preferences.province} ${preferences.country === 'CA' ? 'Provincial' : 'State'} Law`,
        scope: 'provincial'
      });
    }

    // Municipal level
    if (lawCategories[category].jurisdictions.includes('Municipal')) {
      jurisdictions.push({
        id: 'municipal',
        name: 'Municipal/Local',
        scope: 'municipal'
      });
    }

    return jurisdictions;
  };

  const handleCategorySelect = (category) => {
    // Directly complete with category and its scope
    const categoryData = lawCategories[category];
    onComplete({
      category: category,
      lawType: category,
      description: categoryData.description,
      scope: categoryData.scope,
      jurisdiction: preferences?.province || preferences?.country || 'general'
    });
  };

  const handleLawTypeSelect = (lawType) => {
    setSelectedLawType(lawType);
  };

  const handleComplete = () => {
    if (selectedCategory && selectedLawType) {
      onComplete({
        category: selectedCategory,
        lawType: selectedLawType,
        jurisdiction: preferences?.province || preferences?.country || 'general'
      });
    }
  };

  return (
    <div className="law-type-selector">
      <div className="selector-container">
        <div className="selector-header">
          {onBack && (
            <button className="back-btn-header" onClick={onBack}>
              &larr; Back
            </button>
          )}
          <h1 className="legid-logo">LEGID</h1>
          <h2 className="selector-title">Select Your Legal Matter</h2>
          <p className="selector-subtitle">
            Choose the main area of law for your situation
          </p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap', marginTop: '10px' }}>
            {userRole && (
              <div style={{
                padding: '8px 16px',
                background: userRole === 'lawyer' ? 'rgba(255, 107, 107, 0.15)' : 'rgba(0, 212, 255, 0.15)',
                border: `1px solid ${userRole === 'lawyer' ? '#ff6b6b' : '#00d4ff'}`,
                borderRadius: '6px',
                color: userRole === 'lawyer' ? '#ff6b6b' : '#00d4ff',
                fontSize: '13px',
                fontWeight: '600'
              }}>
                {userRole === 'lawyer' ? '⚖️ Lawyer' : '👤 User'}
              </div>
            )}
            {preferences && (
              <div className="jurisdiction-badge">
                <span className="jurisdiction-icon">📍</span>
                <span>
                  {preferences.country === 'CA' ? 'Canada' : 'United States'}
                  {preferences.province && ` - ${preferences.province}`}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Main Categories - Click to go directly to chat */}
        <div className="selection-step">
          <h2 className="step-title">
            <span className="step-number">Select</span>
            Choose Your Legal Area
          </h2>
          <div className="categories-grid">
            {Object.keys(lawCategories).map((category) => (
              <button
                key={category}
                className="category-card"
                onClick={() => handleCategorySelect(category)}
              >
                <div className="category-header">
                  <span className="category-name">{category}</span>
                </div>
                <div className="category-description-text">
                  Click to start with {category.toLowerCase()}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="selector-footer">
          <p className="disclaimer">
            This system provides jurisdiction-specific legal information. 
            All information is sourced from official legal databases and verified case law.
            Not legal advice. Consult a licensed legal professional for your specific situation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LawTypeSelector;
