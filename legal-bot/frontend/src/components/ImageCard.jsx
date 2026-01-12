import React, { useState } from 'react';
import './ImageCard.css';

// Default SVG illustration for legal/DUI case flow
const DefaultIllustration = () => (
  <svg width="100%" height="100%" viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" className="image-card-svg">
    <rect x="0" y="0" width="800" height="320" rx="12" fill="#0e1116"/>
    <rect x="20" y="40" width="760" height="240" rx="12" fill="#121824" stroke="#223047" strokeWidth="1"/>
    
    <text x="40" y="75" fill="#e6edf3" fontFamily="Inter, system-ui" fontSize="18" fontWeight="600">
      DUI Case Flow (Illustration)
    </text>

    <g fontFamily="Inter, system-ui" fontSize="12" fill="#c9d4e3">
      {/* Traffic Stop */}
      <rect x="50" y="110" width="150" height="60" rx="8" fill="#0f172a" stroke="#2b3b55" strokeWidth="1"/>
      <text x="90" y="145" fill="#e6edf3">Traffic stop</text>

      {/* Field Tests */}
      <rect x="230" y="110" width="150" height="60" rx="8" fill="#0f172a" stroke="#2b3b55" strokeWidth="1"/>
      <text x="260" y="135" fill="#e6edf3">Field tests</text>
      <text x="260" y="155" fill="#9fb0c6">Breath / blood</text>

      {/* Charge/Arrest */}
      <rect x="410" y="110" width="150" height="60" rx="8" fill="#0f172a" stroke="#2b3b55" strokeWidth="1"/>
      <text x="440" y="145" fill="#e6edf3">Charge / arrest</text>

      {/* Court Steps */}
      <rect x="590" y="110" width="150" height="60" rx="8" fill="#0f172a" stroke="#2b3b55" strokeWidth="1"/>
      <text x="615" y="135" fill="#e6edf3">Court steps</text>
      <text x="615" y="155" fill="#9fb0c6">Options + timelines</text>

      {/* Connecting Lines */}
      <path d="M200 140 L230 140" stroke="#10a37f" strokeWidth="2"/>
      <path d="M380 140 L410 140" stroke="#10a37f" strokeWidth="2"/>
      <path d="M560 140 L590 140" stroke="#10a37f" strokeWidth="2"/>
    </g>

    <text x="40" y="260" fill="#6b7280" fontFamily="Inter, system-ui" fontSize="11">
      This diagram is informational only. Laws and processes vary by jurisdiction.
    </text>
  </svg>
);

const ImageCard = ({ 
  src, 
  alt = 'Illustration',
  title,
  caption,
  onClick,
  expandable = true 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleClick = () => {
    if (expandable) {
      setIsExpanded(true);
    }
    if (onClick) onClick();
  };

  const handleClose = (e) => {
    e.stopPropagation();
    setIsExpanded(false);
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      setIsExpanded(false);
    }
  };

  return (
    <>
      {/* Image Card */}
      <div className="image-card" onClick={handleClick}>
        <div className="image-card-preview">
          {src && !imageError ? (
            <img 
              src={src} 
              alt={alt}
              onError={() => setImageError(true)}
              className="image-card-img"
            />
          ) : (
            <DefaultIllustration />
          )}
          
          {expandable && (
            <div className="image-card-expand-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
              </svg>
            </div>
          )}
        </div>
        
        {(title || caption) && (
          <div className="image-card-content">
            {title && <h4 className="image-card-title">{title}</h4>}
            {caption && <p className="image-card-caption">{caption}</p>}
          </div>
        )}
      </div>

      {/* Expanded Modal */}
      {isExpanded && (
        <div className="image-modal-backdrop" onClick={handleBackdropClick}>
          <div className="image-modal">
            <button className="image-modal-close" onClick={handleClose}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            
            <div className="image-modal-content">
              {src && !imageError ? (
                <img 
                  src={src} 
                  alt={alt}
                  className="image-modal-img"
                />
              ) : (
                <div className="image-modal-svg-container">
                  <DefaultIllustration />
                </div>
              )}
            </div>
            
            {(title || caption) && (
              <div className="image-modal-footer">
                {title && <h3 className="image-modal-title">{title}</h3>}
                {caption && <p className="image-modal-caption">{caption}</p>}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ImageCard;
