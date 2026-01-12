import React, { useState, useEffect, useRef, useCallback } from 'react';
import './EnhancedLegalResponse.css';
import ImageCard from './ImageCard';

// ============================================
// TIMING CONFIGURATION (Configurable)
// ============================================
const TIMING = {
  TOKEN_DELAY: 15,           // ms between tokens/words
  PARAGRAPH_PAUSE: 250,      // ms pause after paragraph
  SECTION_PAUSE: 400,        // ms pause after heading
  BULLET_PAUSE: 100,         // ms pause after bullet point
  FINAL_PAUSE: 200,          // ms before completion
  THINKING_MIN_DURATION: 800 // minimum thinking animation duration
};

// ============================================
// MARKDOWN PARSER - ChatGPT Style
// ============================================
const parseInlineMarkdown = (text) => {
  if (!text) return null;
  if (typeof text !== 'string') return text;

  const parts = [];
  let lastIndex = 0;
  let partKey = 0;

  // Regex for bold, italic, links, code
  const inlineRegex = /(\*\*[^*]+\*\*)|(\*[^*]+\*)|(`[^`]+`)|(\[[^\]]+\]\([^)]+\))|(https?:\/\/[^\s\)]+)/g;
  let match;

  while ((match = inlineRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={`t-${partKey++}`}>{text.substring(lastIndex, match.index)}</span>);
    }

    const matchedText = match[0];

    if (matchedText.startsWith('**')) {
      const boldText = matchedText.slice(2, -2);
      parts.push(<strong key={`b-${partKey++}`}>{boldText}</strong>);
    } else if (matchedText.startsWith('*') && !matchedText.startsWith('**')) {
      const italicText = matchedText.slice(1, -1);
      parts.push(<em key={`i-${partKey++}`}>{italicText}</em>);
    } else if (matchedText.startsWith('`')) {
      const codeText = matchedText.slice(1, -1);
      parts.push(<code key={`c-${partKey++}`} className="inline-code">{codeText}</code>);
    } else if (matchedText.startsWith('[')) {
      const linkMatch = matchedText.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (linkMatch) {
        parts.push(
          <a key={`l-${partKey++}`} href={linkMatch[2]} target="_blank" rel="noopener noreferrer" className="response-link">
            {linkMatch[1]}
          </a>
        );
      }
    } else if (matchedText.startsWith('http')) {
      parts.push(
        <a key={`u-${partKey++}`} href={matchedText} target="_blank" rel="noopener noreferrer" className="response-link">
          {matchedText}
        </a>
      );
    }

    lastIndex = inlineRegex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(<span key={`t-${partKey++}`}>{text.substring(lastIndex)}</span>);
  }

  return parts.length > 0 ? parts : text;
};

// Full markdown parser
const parseMarkdown = (text) => {
  if (!text) return null;
  if (typeof text !== 'string') return text;

  const lines = text.split('\n');
  const elements = [];
  let currentList = null;
  let listType = null;
  let key = 0;

  const flushList = () => {
    if (currentList && currentList.length > 0) {
      if (listType === 'ordered') {
        elements.push(<ol key={`ol-${key++}`} className="response-list ordered">{currentList}</ol>);
      } else {
        elements.push(<ul key={`ul-${key++}`} className="response-list unordered">{currentList}</ul>);
      }
      currentList = null;
      listType = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();

    if (!trimmedLine) {
      flushList();
      continue;
    }

    // Headers
    if (trimmedLine.startsWith('### ')) {
      flushList();
      elements.push(<h4 key={`h4-${key++}`} className="response-h4">{parseInlineMarkdown(trimmedLine.slice(4))}</h4>);
      continue;
    }
    if (trimmedLine.startsWith('## ')) {
      flushList();
      elements.push(<h3 key={`h3-${key++}`} className="response-h3">{parseInlineMarkdown(trimmedLine.slice(3))}</h3>);
      continue;
    }
    if (trimmedLine.startsWith('# ')) {
      flushList();
      elements.push(<h2 key={`h2-${key++}`} className="response-h2">{parseInlineMarkdown(trimmedLine.slice(2))}</h2>);
      continue;
    }

    // Bold header line
    if (trimmedLine.startsWith('**') && (trimmedLine.endsWith(':**') || trimmedLine.endsWith('**'))) {
      flushList();
      const headerText = trimmedLine.replace(/\*\*/g, '');
      elements.push(<p key={`bh-${key++}`} className="response-bold-header"><strong>{headerText}</strong></p>);
      continue;
    }

    // Numbered list
    const numberedMatch = trimmedLine.match(/^(\d+)\.\s+(.+)/);
    if (numberedMatch) {
      if (listType !== 'ordered') {
        flushList();
        currentList = [];
        listType = 'ordered';
      }
      currentList.push(<li key={`li-${key++}`} className="response-list-item">{parseInlineMarkdown(numberedMatch[2])}</li>);
      continue;
    }

    // Bullet list
    const bulletMatch = trimmedLine.match(/^[-•*]\s+(.+)/);
    if (bulletMatch) {
      if (listType !== 'unordered') {
        flushList();
        currentList = [];
        listType = 'unordered';
      }
      currentList.push(<li key={`li-${key++}`} className="response-list-item">{parseInlineMarkdown(bulletMatch[1])}</li>);
      continue;
    }

    // Horizontal rule
    if (trimmedLine === '---' || trimmedLine === '***') {
      flushList();
      elements.push(<hr key={`hr-${key++}`} className="response-hr" />);
      continue;
    }

    // Regular paragraph
    flushList();
    elements.push(<p key={`p-${key++}`} className="response-paragraph">{parseInlineMarkdown(trimmedLine)}</p>);
  }

  flushList();
  return elements;
};

// ============================================
// THINKING INDICATOR COMPONENT
// ============================================
const ThinkingIndicator = ({ visible }) => {
  if (!visible) return null;
  
  return (
    <div className="thinking-indicator">
      <div className="thinking-dot"></div>
    </div>
  );
};

// ============================================
// BLINKING CURSOR COMPONENT
// ============================================
const BlinkingCursor = ({ visible }) => {
  if (!visible) return null;
  return <span className="blinking-cursor">|</span>;
};

// ============================================
// STREAMING TEXT ANIMATOR
// ============================================
const StreamingText = ({ 
  text, 
  onComplete, 
  isAnimating,
  skipAnimation = false 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const animationRef = useRef(null);
  const indexRef = useRef(0);

  // Calculate delay based on current character context
  const getDelay = useCallback((text, index) => {
    if (index >= text.length) return TIMING.FINAL_PAUSE;
    
    const char = text[index];
    const nextChars = text.substring(index, index + 10);
    const prevChars = text.substring(Math.max(0, index - 5), index);
    
    // After newline + heading markers
    if (prevChars.includes('\n#') || prevChars.includes('\n**')) {
      return TIMING.SECTION_PAUSE;
    }
    
    // After newline (paragraph break)
    if (char === '\n' && text[index + 1] === '\n') {
      return TIMING.PARAGRAPH_PAUSE;
    }
    
    // After bullet or number
    if (prevChars.match(/\n\d+\.\s$/) || prevChars.match(/\n[-•]\s$/)) {
      return TIMING.BULLET_PAUSE;
    }
    
    // Regular character
    return TIMING.TOKEN_DELAY;
  }, []);

  useEffect(() => {
    if (skipAnimation || !text) {
      setDisplayedText(text || '');
      setIsComplete(true);
      if (onComplete) onComplete();
      return;
    }

    if (!isAnimating) return;

    indexRef.current = 0;
    setDisplayedText('');
    setIsComplete(false);

    const animate = () => {
      if (indexRef.current < text.length) {
        // Add multiple characters at once for smoother animation
        const charsToAdd = Math.min(2, text.length - indexRef.current);
        indexRef.current += charsToAdd;
        setDisplayedText(text.substring(0, indexRef.current));
        
        const delay = getDelay(text, indexRef.current);
        animationRef.current = setTimeout(animate, delay);
      } else {
        setIsComplete(true);
        if (onComplete) onComplete();
      }
    };

    // Start animation
    animationRef.current = setTimeout(animate, TIMING.TOKEN_DELAY);

    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, [text, isAnimating, skipAnimation, onComplete, getDelay]);

  // Render with cursor
  return (
    <div className="streaming-text-container">
      {isComplete ? (
        parseMarkdown(displayedText)
      ) : (
        <div className="streaming-text">
          <span className="streaming-content">{displayedText}</span>
          <BlinkingCursor visible={!isComplete} />
        </div>
      )}
    </div>
  );
};

// ============================================
// MAIN ENHANCED LEGAL RESPONSE COMPONENT
// ============================================
const EnhancedLegalResponse = ({ response, isNewMessage = true }) => {
  const [phase, setPhase] = useState('thinking'); // 'thinking' | 'streaming' | 'complete'
  const [showThinking, setShowThinking] = useState(true);
  const thinkingTimerRef = useRef(null);

  // Get answer text
  const answerText = response?.answer || response?.content || '';
  
  // Check if response has an illustration/image
  const hasIllustration = response?.showIllustration || 
                          response?.illustration || 
                          answerText.toLowerCase().includes('illustration:') ||
                          answerText.toLowerCase().includes('diagram:');
  
  // Check if this is a welcome message or should skip animation
  const shouldSkipAnimation = response?.isWelcome || !isNewMessage || !answerText;

  useEffect(() => {
    if (shouldSkipAnimation) {
      setPhase('complete');
      setShowThinking(false);
      return;
    }

    // Start with thinking phase
    setPhase('thinking');
    setShowThinking(true);

    // Minimum thinking duration for smooth UX
    thinkingTimerRef.current = setTimeout(() => {
      setShowThinking(false);
      setPhase('streaming');
    }, TIMING.THINKING_MIN_DURATION);

    return () => {
      if (thinkingTimerRef.current) {
        clearTimeout(thinkingTimerRef.current);
      }
    };
  }, [answerText, shouldSkipAnimation]);

  const handleStreamComplete = useCallback(() => {
    setPhase('complete');
  }, []);

  // Render based on phase
  return (
    <div className={`enhanced-legal-response phase-${phase}`}>
      {/* Thinking indicator - blinking dot */}
      {phase === 'thinking' && showThinking && (
        <ThinkingIndicator visible={true} />
      )}

      {/* Streaming/Complete content */}
      {(phase === 'streaming' || phase === 'complete') && !shouldSkipAnimation && (
        <div className="response-content">
          {answerText ? (
            <StreamingText
              text={answerText}
              isAnimating={phase === 'streaming'}
              skipAnimation={phase === 'complete'}
              onComplete={handleStreamComplete}
            />
          ) : (
            <p className="no-response">No response received.</p>
          )}
        </div>
      )}

      {/* Show instantly for skipped animations */}
      {shouldSkipAnimation && answerText && (
        <div className="response-content">
          {parseMarkdown(answerText)}
        </div>
      )}

      {/* Image Card - "Explain with image" feature */}
      {phase === 'complete' && hasIllustration && (
        <ImageCard
          src={response?.illustrationSrc}
          title={response?.illustrationTitle || "Case Flow Illustration"}
          caption={response?.illustrationCaption || "This diagram is informational only. Laws and processes vary by jurisdiction."}
        />
      )}
    </div>
  );
};

export default EnhancedLegalResponse;
