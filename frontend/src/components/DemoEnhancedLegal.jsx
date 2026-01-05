import React from 'react';
import EnhancedLegalResponse from './EnhancedLegalResponse';
import './DemoEnhancedLegal.css';

const DemoEnhancedLegal = () => {
  // Demo legal response data
  const demoResponse = {
    answer: `🎯 OFFENSE: Landlord negligence - Major repairs not done
   Question: My landlord won't fix major repairs in my Ontario apartment. What can I do?

💡 SOLUTION:
   1. Request repairs in writing within 7 days
   2. Emergency repairs: arrange and deduct from rent (up to $500/month)
   3. Non-emergency: landlord has 7 days to respond
   4. Repair deduction: proportional to uninhabitability
   5. Rent reduction application to Landlord and Tenant Board
   6. File LTB application (free, binding decisions)
   7. Termination of tenancy if landlord breaches obligations
   8. Appeal to Divisional Court if needed

📚 REFERENCE:
   [1] Ontario Residential Tenancies Act - Page: 1 | Relevance: 0.940
   [2] Landlord and Tenant Board Procedures - Page: 1 | Relevance: 0.920

📊 STATISTICS:
   Confidence Score: 0.920
   Citations Found: 2
   Document Chunks Used: 12`,
    citations: [
      {
        filename: "Ontario Residential Tenancies Act",
        page: 1,
        score: 0.94
      },
      {
        filename: "Landlord and Tenant Board Procedures",
        page: 1,
        score: 0.92
      }
    ],
    confidence: 0.92,
    chunks_used: 12
  };

  const demoResponse2 = {
    answer: `🎯 OFFENSE: SPEEDING TICKET - 20 km/h over limit in Ontario
   Question: I got a speeding ticket in Ontario for going 20 km/h over the limit. What should I do?

💡 SOLUTION:
   1. Pay fine within 15 days: 50% reduction for most offences
   2. Pay full fine within 30 days to avoid court
   3. Request trial by mail, phone, or in person
   4. Trial must be requested within 15 days
   5. Can plead guilty with explanation for reduced fine
   6. Not guilty plea leads to court appearance
   7. Speed timing device malfunction (defense)
   8. Emergency situation (defense)

📚 REFERENCE:
   [1] Ontario Highway Traffic Act - Page: 1 | Relevance: 0.950
   [2] Ontario Traffic Ticket Procedures - Page: 1 | Relevance: 0.925
   [3] Ontario Court Procedures Guide - Page: 1 | Relevance: 0.900

📊 STATISTICS:
   Confidence Score: 0.925
   Citations Found: 3
   Document Chunks Used: 15`,
    citations: [
      {
        filename: "Ontario Highway Traffic Act",
        page: 1,
        score: 0.95
      },
      {
        filename: "Ontario Traffic Ticket Procedures",
        page: 1,
        score: 0.925
      },
      {
        filename: "Ontario Court Procedures Guide",
        page: 1,
        score: 0.90
      }
    ],
    confidence: 0.925,
    chunks_used: 15
  };

  return (
    <div className="demo-enhanced-legal">
      <div className="demo-header">
        <h1>🎯 Enhanced Legal Response Demo</h1>
        <p>This is how legal questions will be displayed in your PLAZA-AI frontend</p>
        <p><strong>Format:</strong> OFFENSE ------> SOLUTION ------> REFERENCE</p>
      </div>

      <div className="demo-examples">
        <div className="demo-example">
          <h2>Example 1: Landlord-Tenant Dispute</h2>
          <div className="chat-message assistant">
            <EnhancedLegalResponse response={demoResponse} />
          </div>
        </div>

        <div className="demo-example">
          <h2>Example 2: Traffic Violation</h2>
          <div className="chat-message assistant">
            <EnhancedLegalResponse response={demoResponse2} />
          </div>
        </div>
      </div>

      <div className="demo-features">
        <h2>✨ Enhanced Features</h2>
        <div className="features-grid">
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <h3>Clear Problem Identification</h3>
            <p>Every legal issue is clearly stated as an "OFFENSE"</p>
          </div>

          <div className="feature-item">
            <span className="feature-icon">💡</span>
            <h3>Practical Solutions</h3>
            <p>Numbered list of actionable remedies and next steps</p>
          </div>

          <div className="feature-item">
            <span className="feature-icon">📚</span>
            <h3>Legal References</h3>
            <p>Citations with relevance scores and page numbers</p>
          </div>

          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <h3>Response Statistics</h3>
            <p>Confidence scores and analysis metrics</p>
          </div>
        </div>
      </div>

      <div className="demo-activation">
        <h2>🚀 How to Activate</h2>
        <div className="activation-steps">
          <div className="step">
            <span className="step-number">1</span>
            <div className="step-content">
              <h3>Start Backend</h3>
              <code>cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000</code>
            </div>
          </div>

          <div className="step">
            <span className="step-number">2</span>
            <div className="step-content">
              <h3>Ingest Enhanced Datasets</h3>
              <code>python ingest_all_documents.py</code>
            </div>
          </div>

          <div className="step">
            <span className="step-number">3</span>
            <div className="step-content">
              <h3>Start Frontend</h3>
              <code>cd frontend && npm start</code>
            </div>
          </div>

          <div className="step">
            <span className="step-number">4</span>
            <div className="step-content">
              <h3>Ask Legal Questions</h3>
              <p>Get structured OFFENSE → SOLUTION → REFERENCE responses!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoEnhancedLegal;