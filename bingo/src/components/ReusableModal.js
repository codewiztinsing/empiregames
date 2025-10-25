import React from 'react';
import './ReusableModal.css';

const ReusableModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  showCloseButton = true,
  closeOnOverlayClick = true,
  size = 'medium', // small, medium, large
  className = ''
}) => {
  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className={`reusable-modal-overlay ${className}`}
      onClick={handleOverlayClick}
    >
      <div className={`reusable-modal-content reusable-modal-${size}`}>
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="reusable-modal-header">
            {title && (
              <div className="reusable-modal-title">
                {title}
              </div>
            )}
            {showCloseButton && (
              <button 
                className="reusable-modal-close"
                onClick={onClose}
                aria-label="Close modal"
              >
                ×
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="reusable-modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default ReusableModal;
