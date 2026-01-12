import React, { useState } from 'react';
import './DescribeSituation.css';

const DescribeSituation = ({ preferences, onComplete, onBack }) => {
  const [situation, setSituation] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [step, setStep] = useState(1);

  const situationCategories = [
    {
      id: 'immigration',
      title: 'Immigration Matter',
      description: 'Visa, work permits, permanent residence, citizenship',
      icon: 'IMMIGRATION',
      questions: [
        'What type of immigration application are you dealing with?',
        'What is your current immigration status?',
        'What province/territory do you want to settle in?',
        'Do you have a job offer or family in Canada?'
      ]
    },
    {
      id: 'criminal',
      title: 'Criminal Matter',
      description: 'Charges, arrests, court proceedings, appeals',
      icon: 'CRIMINAL',
      questions: [
        'What are you charged with?',
        'When did the incident occur?',
        'Have you been arrested or released on bail?',
        'Do you have a court date scheduled?'
      ]
    },
    {
      id: 'family',
      title: 'Family Matter',
      description: 'Divorce, custody, support, property division',
      icon: 'FAMILY',
      questions: [
        'What family law issue are you facing?',
        'Are you married or in a common-law relationship?',
        'Do you have children? What are their ages?',
        'Have you and your spouse separated?'
      ]
    },
    {
      id: 'employment',
      title: 'Employment Matter',
      description: 'Wrongful dismissal, workplace harassment, contracts',
      icon: 'EMPLOYMENT',
      questions: [
        'What is your employment situation?',
        'How long have you worked for this employer?',
        'Were you terminated or did you resign?',
        'Do you have an employment contract?'
      ]
    },
    {
      id: 'traffic',
      title: 'Traffic Matter',
      description: 'Tickets, suspensions, accidents, demerit points',
      icon: 'TRAFFIC',
      questions: [
        'What traffic offence were you charged with? (Speeding, Careless Driving, Distracted Driving, Impaired Driving, etc.)',
        'When and where did this occur? (Date, time, location, road conditions)',
        'If speeding: What was the speed limit and your actual speed?',
        'If distracted driving: What were you doing? (Phone use, eating, other)',
        'If impaired driving: What was your Blood Alcohol Content (BAC) or THC level? (Legal limit: 0.08% BAC, 2-5ng THC)',
        'Were you given a roadside test? What were the results?',
        'Do you have prior traffic convictions or demerit points?',
        'Have you received a court date or summons?'
      ]
    },
    {
      id: 'business',
      title: 'Business Matter',
      description: 'Contracts, disputes, incorporation, compliance',
      icon: 'BUSINESS',
      questions: [
        'What type of business issue do you have?',
        'Is your business incorporated?',
        'What province is your business registered in?',
        'Are you involved in a dispute?'
      ]
    },
    {
      id: 'real_estate',
      title: 'Real Estate Matter',
      description: 'Property purchase/sale, landlord-tenant, disputes',
      icon: 'REAL ESTATE',
      questions: [
        'What is your real estate issue?',
        'Are you buying, selling, or renting?',
        'Where is the property located?',
        'Do you have a signed agreement?'
      ]
    },
    {
      id: 'other',
      title: 'Other Legal Matter',
      description: 'Tax, wills, estates, health law, or other issues',
      icon: 'OTHER',
      questions: [
        'Please describe your legal issue',
        'When did this issue begin?',
        'Have you sought legal advice before?',
        'What outcome are you hoping for?'
      ]
    }
  ];

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setStep(2);
  };

  const handleComplete = () => {
    onComplete({
      category: selectedCategory,
      description: situation,
      preferences: preferences
    });
  };

  return (
    <div className="describe-situation">
      <div className="situation-container">
        <div className="situation-header">
          <h1>Describe Your Legal Situation</h1>
          <p className="situation-subtitle">
            Help us understand your situation so we can provide the most relevant legal information
          </p>
          {preferences && (
            <div className="location-badge">
              <span>Location: {preferences.country === 'CA' ? 'Canada' : 'United States'}</span>
              {preferences.province && <span> - {preferences.province}</span>}
            </div>
          )}
        </div>

        {step === 1 && (
          <div className="step-content">
            <h2 className="step-title">
              <span className="step-number">Step 1</span>
              What type of legal matter do you need help with?
            </h2>

            <div className="categories-grid">
              {situationCategories.map((category) => (
                <button
                  key={category.id}
                  className="category-card"
                  onClick={() => handleCategorySelect(category)}
                >
                  <div className="category-icon">{category.icon}</div>
                  <h3 className="category-title">{category.title}</h3>
                  <p className="category-description">{category.description}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 2 && selectedCategory && (
          <div className="step-content">
            <button className="back-btn" onClick={() => {
              setStep(1);
              setSelectedCategory(null);
              setSituation('');
            }}>
              &larr; Back to Categories
            </button>

            <h2 className="step-title">
              <span className="step-number">Step 2</span>
              Tell us about your {selectedCategory.title.toLowerCase()}
            </h2>

            <div className="situation-form">
              <div className="guided-questions">
                <h3>Consider these questions as you describe your situation:</h3>
                <ul>
                  {selectedCategory.questions.map((question, idx) => (
                    <li key={idx}>{question}</li>
                  ))}
                </ul>
              </div>

              <div className="text-input-section">
                <label htmlFor="situation">Describe your situation in detail:</label>
                <textarea
                  id="situation"
                  className="situation-textarea"
                  value={situation}
                  onChange={(e) => setSituation(e.target.value)}
                  placeholder="Please provide as much detail as possible. Include dates, locations, speeds, meter readings (BAC/THC levels), road conditions, weather, and any important facts. For impaired driving cases, include breathalyzer or drug test results."
                  rows={12}
                />
                <div className="char-count">
                  {situation.length} characters
                </div>
              </div>

              <div className="form-actions">
                <button
                  className="continue-btn"
                  onClick={handleComplete}
                  disabled={situation.length < 10}
                >
                  Continue to Legal Assistant
                  <span className="arrow">&rarr;</span>
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="situation-footer">
          <div className="privacy-notice">
            <h4>Privacy Notice</h4>
            <p>Your information is used only to provide relevant legal information. We do not share your details with third parties.</p>
          </div>
          <div className="disclaimer-notice">
            <h4>Important</h4>
            <p>This is general legal information, not legal advice. For advice about your specific situation, consult a licensed lawyer.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DescribeSituation;
