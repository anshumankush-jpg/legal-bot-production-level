import React from 'react';
import './LegalResponse.css';

/**
 * Format legal response text with proper HTML styling
 * Converts markdown-style formatting to HTML for ChatGPT-like appearance
 * NO VISIBLE STARS - all markdown converted to clean HTML
 */
function formatLegalResponse(text) {
  if (!text) return '';
  
  let formatted = text;
  
  // Convert **bold** to <strong> FIRST (before headers to handle bold in headers)
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Convert ### headers to <h3>
  formatted = formatted.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
  formatted = formatted.replace(/^## (.*?)$/gm, '<h3>$1</h3>');
  
  // Convert #### headers to <h4>
  formatted = formatted.replace(/^#### (.*?)$/gm, '<h4>$1</h4>');
  
  // Convert links [text](url) to <a>
  formatted = formatted.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Remove any remaining asterisks that might be used for emphasis
  formatted = formatted.replace(/\*/g, '');
  
  // Convert bullet points
  const lines = formatted.split('\n');
  let inList = false;
  let listType = null;
  const processedLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    
    // Unordered list (- item)
    if (trimmed.match(/^- /)) {
      if (!inList || listType !== 'ul') {
        if (inList) processedLines.push(`</${listType}>`);
        processedLines.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      processedLines.push(`<li>${trimmed.substring(2)}</li>`);
    }
    // Ordered list (1. item)
    else if (trimmed.match(/^\d+\. /)) {
      if (!inList || listType !== 'ol') {
        if (inList) processedLines.push(`</${listType}>`);
        processedLines.push('<ol>');
        inList = true;
        listType = 'ol';
      }
      processedLines.push(`<li>${trimmed.replace(/^\d+\. /, '')}</li>`);
    }
    // Not a list item
    else {
      if (inList) {
        processedLines.push(`</${listType}>`);
        inList = false;
        listType = null;
      }
      processedLines.push(line);
    }
  }
  
  // Close any open list
  if (inList) {
    processedLines.push(`</${listType}>`);
  }
  
  formatted = processedLines.join('\n');
  
  // Convert paragraphs (double newlines)
  const paragraphs = formatted.split('\n\n');
  formatted = paragraphs.map(para => {
    const trimmed = para.trim();
    // Don't wrap if already HTML tag
    if (trimmed.startsWith('<') || !trimmed) {
      return para;
    }
    // Don't wrap single newlines within paragraphs
    return `<p>${para.replace(/\n/g, '<br/>')}</p>`;
  }).join('\n\n');
  
  // Detect and style disclaimer
  if (formatted.includes('educational purposes only') || 
      formatted.includes('does not constitute legal advice')) {
    formatted = formatted.replace(
      /(This information is for educational purposes only.*?attorney.*?\.)/gi,
      '<div class="disclaimer">$1</div>'
    );
  }
  
  // Style key information boxes
  formatted = formatted.replace(
    /\*\*Key Points?:\*\*/gi,
    '<div class="key-info"><strong>Key Points:</strong>'
  );
  
  // Style warnings
  formatted = formatted.replace(
    /\*\*Warning:\*\*/gi,
    '<div class="warning"><strong>Warning:</strong>'
  );
  
  // Close any open divs (simple approach)
  const openDivs = (formatted.match(/<div class="(key-info|warning)">/g) || []).length;
  const closeDivs = (formatted.match(/<\/div>/g) || []).length;
  if (openDivs > closeDivs) {
    for (let i = 0; i < (openDivs - closeDivs); i++) {
      formatted += '</div>';
    }
  }
  
  // Convert horizontal rules
  formatted = formatted.replace(/^---$/gm, '<hr/>');
  
  return formatted;
}

/**
 * LegalResponse Component
 * Displays formatted legal chatbot responses with ChatGPT-like styling
 */
function LegalResponse({ content, role = 'assistant' }) {
  if (role === 'user') {
    return (
      <div className="message user">
        <div className="user-message">{content}</div>
      </div>
    );
  }
  
  const formattedContent = formatLegalResponse(content);
  
  return (
    <div className="message assistant">
      <div 
        className="bot-response"
        dangerouslySetInnerHTML={{ __html: formattedContent }}
      />
    </div>
  );
}

/**
 * TypingIndicator Component
 * Shows animated dots while bot is thinking
 */
export function TypingIndicator() {
  return (
    <div className="message assistant">
      <div className="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
}

export default LegalResponse;
