import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes, faGift, faPercent, faClock, faStar } from '@fortawesome/free-solid-svg-icons';
import './PromotionModal.css';

const PromotionModal = ({ promotion, onClose, onClaim, onTrackView, onTrackClick }) => {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (promotion) {
      setIsVisible(true);
      setIsAnimating(true);
      
      // Track view
      if (onTrackView) {
        onTrackView(promotion.id);
      }
      
      // Auto-hide after 10 seconds if not interacted with
      const autoHideTimer = setTimeout(() => {
        if (isVisible) {
          handleClose();
        }
      }, 10000);
      
      return () => clearTimeout(autoHideTimer);
    }
  }, [promotion]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setIsVisible(false);
      onClose();
    }, 300);
  };

  const handleClaim = () => {
    if (onTrackClick) {
      onTrackClick(promotion.id);
    }
    if (onClaim) {
      onClaim(promotion);
    }
    handleClose();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (!isVisible || !promotion) return null;

  return (
    <div className={`promotion-modal-overlay ${isAnimating ? 'show' : 'hide'}`}>
      <div className={`promotion-modal ${isAnimating ? 'show' : 'hide'}`}>
        {/* Close Button */}
        <button className="promotion-close-btn" onClick={handleClose}>
          <FontAwesomeIcon icon={faTimes} />
        </button>

        {/* Promotion Header */}
        <div className="promotion-header">
          <div className="promotion-icon">
            <FontAwesomeIcon icon={faGift} />
          </div>
          <div className="promotion-title-section">
            <h2 className="promotion-title">{promotion.title}</h2>
            <div className="promotion-badge">
              <FontAwesomeIcon icon={faStar} />
              <span>{t('promotion.exclusive')}</span>
            </div>
          </div>
        </div>

        {/* Promotion Image */}
        {promotion.banner_image_url && (
          <div className="promotion-image-container">
            <img 
              src={promotion.banner_image_url} 
              alt={promotion.title}
              className="promotion-image"
            />
          </div>
        )}

        {/* Promotion Content */}
        <div className="promotion-content">
          {promotion.description && (
            <p className="promotion-description">{promotion.description}</p>
          )}

          {/* Promotion Details */}
          <div className="promotion-details">
            {promotion.discount_percentage && (
              <div className="promotion-detail-item">
                <FontAwesomeIcon icon={faPercent} className="detail-icon" />
                <div className="detail-content">
                  <span className="detail-label">{t('promotion.discount')}</span>
                  <span className="detail-value">{promotion.discount_percentage}%</span>
                </div>
              </div>
            )}

            {promotion.bonus_amount && (
              <div className="promotion-detail-item">
                <FontAwesomeIcon icon={faGift} className="detail-icon" />
                <div className="detail-content">
                  <span className="detail-label">{t('promotion.bonus')}</span>
                  <span className="detail-value">{promotion.bonus_amount} ETB</span>
                </div>
              </div>
            )}

            {promotion.minimum_deposit && (
              <div className="promotion-detail-item">
                <FontAwesomeIcon icon={faClock} className="detail-icon" />
                <div className="detail-content">
                  <span className="detail-label">{t('promotion.minimumDeposit')}</span>
                  <span className="detail-value">{promotion.minimum_deposit} ETB</span>
                </div>
              </div>
            )}
          </div>

          {/* Valid Until */}
          {promotion.end_date && (
            <div className="promotion-validity">
              <FontAwesomeIcon icon={faClock} />
              <span>{t('promotion.validUntil')}: {formatDate(promotion.end_date)}</span>
            </div>
          )}
        </div>

        {/* Promotion Actions */}
        <div className="promotion-actions">
          <button className="promotion-claim-btn" onClick={handleClaim}>
            <FontAwesomeIcon icon={faGift} />
            <span>{t('promotion.claimNow')}</span>
          </button>
          <button className="promotion-close-action-btn" onClick={handleClose}>
            {t('promotion.close')}
          </button>
        </div>

        {/* Terms and Conditions */}
        <div className="promotion-terms">
          <small>{t('promotion.termsAndConditions')}</small>
        </div>
      </div>
    </div>
  );
};

export default PromotionModal;
