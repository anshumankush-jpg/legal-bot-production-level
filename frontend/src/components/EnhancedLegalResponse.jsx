import React from 'react';
import './EnhancedLegalResponse.css';

const EnhancedLegalResponse = ({ response }) => {
  // Parse the structured response
  const parseStructuredResponse = (answer) => {
    const lines = answer.split('\n');
    let currentSection = null;
    const sections = {
      offense: [],
      solution: [],
      reference: [],
      statistics: []
    };

    for (const line of lines) {
      const trimmedLine = line.trim();

      if (trimmedLine.includes('🎯 OFFENSE:') || trimmedLine.includes('OFFENSE:')) {
        currentSection = 'offense';
        continue;
      } else if (trimmedLine.includes('💡 SOLUTION:') || trimmedLine.includes('SOLUTION:')) {
        currentSection = 'solution';
        continue;
      } else if (trimmedLine.includes('📚 REFERENCE:') || trimmedLine.includes('REFERENCE:')) {
        currentSection = 'reference';
        continue;
      } else if (trimmedLine.includes('📊 STATISTICS:') || trimmedLine.includes('STATISTICS:')) {
        currentSection = 'statistics';
        continue;
      }

      if (currentSection && trimmedLine && !trimmedLine.startsWith('---')) {
        sections[currentSection].push(trimmedLine);
      }
    }

    return sections;
  };

  // Get answer from either response.answer or response.content
  const answerText = response.answer || response.content || '';
  const sections = parseStructuredResponse(answerText);

  return (
    <div className="enhanced-legal-response">
      {/* Offense Section */}
      {sections.offense.length > 0 && (
        <div className="response-section offense-section">
          <div className="section-header">
            <span className="section-icon">🎯</span>
            <h3>OFFENSE</h3>
          </div>
          <div className="section-content">
            {sections.offense.map((line, index) => (
              <p key={index} className="offense-text">{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* Solution Section */}
      {sections.solution.length > 0 && (
        <div className="response-section solution-section">
          <div className="section-header">
            <span className="section-icon">💡</span>
            <h3>SOLUTION</h3>
          </div>
          <div className="section-content">
            <ol className="solution-list">
              {sections.solution.map((line, index) => {
                // Remove numbering if present (e.g., "1. " at start)
                const cleanLine = line.replace(/^\d+\.\s*/, '').trim();
                if (cleanLine && cleanLine.length > 10) { // Filter out very short fragments
                  return <li key={index} className="solution-item">{cleanLine}</li>;
                }
                return null;
              }).filter(Boolean)}
            </ol>
          </div>
        </div>
      )}

      {/* Reference Section */}
      {(sections.reference.length > 0 || (response.citations && response.citations.length > 0)) && (
        <div className="response-section reference-section">
          <div className="section-header">
            <span className="section-icon">📚</span>
            <h3>REFERENCE</h3>
          </div>
          <div className="section-content">
            {/* Structured references from response */}
            {sections.reference.map((line, index) => {
              if (line.includes('[') && line.includes(']')) {
                return <p key={index} className="reference-item">{line}</p>;
              }
              return null;
            }).filter(Boolean)}

            {/* Citations from API response */}
            {response.citations && response.citations.map((citation, index) => (
              <div key={index} className="citation-item">
                <span className="citation-number">[{index + 1}]</span>
                <span className="citation-filename">
                  {citation.filename || 'Unknown'} {citation.page ? `(Page ${citation.page})` : ''}
                </span>
                {citation.score && (
                  <span className="citation-score">
                    Relevance: {(citation.score * 100).toFixed(1)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics Section */}
      {sections.statistics.length > 0 && (
        <div className="response-section statistics-section">
          <div className="section-header">
            <span className="section-icon">📊</span>
            <h3>STATISTICS</h3>
          </div>
          <div className="section-content">
            {sections.statistics.map((line, index) => (
              <p key={index} className="statistics-item">{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* Fallback for unstructured responses */}
      {sections.offense.length === 0 && sections.solution.length === 0 && sections.reference.length === 0 && (
        <div className="fallback-response">
          {answerText && answerText.trim() ? (
            <div className="message-text">
              {answerText.split('\n').map((line, index) => (
                <p key={index}>{line || '\u00A0'}</p>
              ))}
            </div>
          ) : (
            <p className="no-response">No response received. Please try again.</p>
          )}
          {response.citations && response.citations.length > 0 && (
            <div className="fallback-citations">
              <h4>Sources:</h4>
              {response.citations.map((citation, index) => (
                <p key={index}>
                  {citation.filename || 'Unknown'} {citation.page ? `(Page ${citation.page})` : ''}
                </p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Response metadata */}
      <div className="response-metadata">
        {response.confidence && (
          <span className="confidence-badge">
            Confidence: {(response.confidence * 100).toFixed(1)}%
          </span>
        )}
        {response.chunks_used && (
          <span className="chunks-badge">
            Analyzed {response.chunks_used} document chunks
          </span>
        )}
      </div>
    </div>
  );
};

export default EnhancedLegalResponse;