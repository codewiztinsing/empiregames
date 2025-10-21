import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faTimes, 
  faGift, 
  faPercent, 
  faClock, 
  faStar, 
  faEye, 
  faMousePointer,
  faCalendarAlt,
  faEdit,
  faTrash,
  faPlay,
  faPause,
  faPlus,
  faFilter,
  faSearch,
  faChartLine,
  faUsers,
  faBullhorn
} from '@fortawesome/free-solid-svg-icons';
import './PromotionSidebar.css';

const PromotionSidebar = ({ isOpen, onClose, onSendPromotion, onTrackPromotion }) => {
  const { t } = useTranslation();
  const [promotions, setPromotions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedPromotion, setSelectedPromotion] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [stats, setStats] = useState({
    totalPromotions: 0,
    activePromotions: 0,
    totalViews: 0,
    totalClicks: 0
  });

  // Fetch promotions from API
  const fetchPromotions = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/promotions/admin/list', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('telegram_auth_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPromotions(data.promotions || []);
        
        // Calculate stats
        const totalPromotions = data.promotions?.length || 0;
        const activePromotions = data.promotions?.filter(p => p.status === 'active').length || 0;
        const totalViews = data.promotions?.reduce((sum, p) => sum + (p.view_count || 0), 0) || 0;
        const totalClicks = data.promotions?.reduce((sum, p) => sum + (p.click_count || 0), 0) || 0;
        
        setStats({
          totalPromotions,
          activePromotions,
          totalViews,
          totalClicks
        });
      }
    } catch (error) {
      console.error('Error fetching promotions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchPromotions();
    }
  }, [isOpen]);

  // Filter promotions based on search and status
  const filteredPromotions = promotions.filter(promotion => {
    const matchesSearch = promotion.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         promotion.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || promotion.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const handleSendPromotion = async (promotion) => {
    try {
      const response = await fetch('/api/v1/promotions/send', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('telegram_auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ promotion_id: promotion.id })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Trigger WebSocket send
          if (onSendPromotion) {
            onSendPromotion(promotion);
          }
          alert(`Promotion "${promotion.title}" sent successfully!`);
          fetchPromotions(); // Refresh data
        } else {
          alert(`Failed to send promotion: ${data.message}`);
        }
      }
    } catch (error) {
      console.error('Error sending promotion:', error);
      alert('Failed to send promotion');
    }
  };

  const handleTrackPromotion = async (promotionId, action) => {
    try {
      const endpoint = action === 'view' ? 'track-view' : 'track-click';
      await fetch(`/api/v1/promotions/${endpoint}/${promotionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('telegram_auth_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (onTrackPromotion) {
        onTrackPromotion(promotionId, action);
      }
    } catch (error) {
      console.error(`Error tracking promotion ${action}:`, error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#4caf50';
      case 'inactive': return '#f44336';
      case 'scheduled': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getPromotionTypeIcon = (type) => {
    switch (type) {
      case 'banner': return faBullhorn;
      case 'popup': return faGift;
      case 'notification': return faStar;
      default: return faGift;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="promotion-sidebar-overlay" onClick={onClose}>
      <div className="promotion-sidebar" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="promotion-sidebar-header">
          <div className="sidebar-title">
            <FontAwesomeIcon icon={faBullhorn} />
            <span>{t('promotion.management')}</span>
          </div>
          <button className="close-btn" onClick={onClose}>
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>

        {/* Stats Cards */}
        <div className="promotion-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <FontAwesomeIcon icon={faGift} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.totalPromotions}</div>
              <div className="stat-label">{t('promotion.total')}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon active">
              <FontAwesomeIcon icon={faPlay} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.activePromotions}</div>
              <div className="stat-label">{t('promotion.active')}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon views">
              <FontAwesomeIcon icon={faEye} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.totalViews}</div>
              <div className="stat-label">{t('promotion.views')}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon clicks">
              <FontAwesomeIcon icon={faMousePointer} />
            </div>
            <div className="stat-content">
              <div className="stat-number">{stats.totalClicks}</div>
              <div className="stat-label">{t('promotion.clicks')}</div>
            </div>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="promotion-controls">
          <div className="search-box">
            <FontAwesomeIcon icon={faSearch} />
            <input
              type="text"
              placeholder={t('promotion.search')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="filter-box">
            <FontAwesomeIcon icon={faFilter} />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">{t('promotion.allStatus')}</option>
              <option value="active">{t('promotion.active')}</option>
              <option value="inactive">{t('promotion.inactive')}</option>
              <option value="scheduled">{t('promotion.scheduled')}</option>
            </select>
          </div>
        </div>

        {/* Create New Button */}
        <div className="create-promotion-section">
          <button 
            className="create-promotion-btn"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            <FontAwesomeIcon icon={faPlus} />
            <span>{t('promotion.createNew')}</span>
          </button>
        </div>

        {/* Promotions List */}
        <div className="promotions-list">
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <span>{t('common.loading')}</span>
            </div>
          ) : (
            filteredPromotions.map((promotion) => (
              <div 
                key={promotion.id} 
                className={`promotion-item ${selectedPromotion?.id === promotion.id ? 'selected' : ''}`}
                onClick={() => setSelectedPromotion(promotion)}
              >
                <div className="promotion-item-header">
                  <div className="promotion-type">
                    <FontAwesomeIcon icon={getPromotionTypeIcon(promotion.promotion_type)} />
                  </div>
                  <div className="promotion-title">{promotion.title}</div>
                  <div 
                    className="promotion-status"
                    style={{ backgroundColor: getStatusColor(promotion.status) }}
                  >
                    {promotion.status}
                  </div>
                </div>
                
                <div className="promotion-item-content">
                  <p className="promotion-description">{promotion.description}</p>
                  
                  <div className="promotion-details">
                    {promotion.discount_percentage && (
                      <div className="detail-item">
                        <FontAwesomeIcon icon={faPercent} />
                        <span>{promotion.discount_percentage}% {t('promotion.discount')}</span>
                      </div>
                    )}
                    {promotion.bonus_amount && (
                      <div className="detail-item">
                        <FontAwesomeIcon icon={faGift} />
                        <span>{promotion.bonus_amount} ETB {t('promotion.bonus')}</span>
                      </div>
                    )}
                    {promotion.end_date && (
                      <div className="detail-item">
                        <FontAwesomeIcon icon={faCalendarAlt} />
                        <span>{t('promotion.validUntil')}: {formatDate(promotion.end_date)}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="promotion-metrics">
                    <div className="metric">
                      <FontAwesomeIcon icon={faEye} />
                      <span>{promotion.view_count || 0}</span>
                    </div>
                    <div className="metric">
                      <FontAwesomeIcon icon={faMousePointer} />
                      <span>{promotion.click_count || 0}</span>
                    </div>
                  </div>
                </div>
                
                <div className="promotion-item-actions">
                  {promotion.status === 'active' && (
                    <button 
                      className="action-btn send-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSendPromotion(promotion);
                      }}
                    >
                      <FontAwesomeIcon icon={faPlay} />
                      <span>{t('promotion.send')}</span>
                    </button>
                  )}
                  <button 
                    className="action-btn edit-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle edit
                    }}
                  >
                    <FontAwesomeIcon icon={faEdit} />
                  </button>
                  <button 
                    className="action-btn delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Handle delete
                    }}
                  >
                    <FontAwesomeIcon icon={faTrash} />
                  </button>
                </div>
              </div>
            ))
          )}
          
          {!loading && filteredPromotions.length === 0 && (
            <div className="empty-state">
              <FontAwesomeIcon icon={faGift} />
              <p>{t('promotion.noPromotions')}</p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button 
            className="quick-action-btn"
            onClick={() => {
              // Send all active promotions
              const activePromotions = promotions.filter(p => p.status === 'active');
              activePromotions.forEach(promotion => handleSendPromotion(promotion));
            }}
          >
            <FontAwesomeIcon icon={faBullhorn} />
            <span>{t('promotion.sendAll')}</span>
          </button>
          <button 
            className="quick-action-btn"
            onClick={fetchPromotions}
          >
            <FontAwesomeIcon icon={faChartLine} />
            <span>{t('promotion.refresh')}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PromotionSidebar;
