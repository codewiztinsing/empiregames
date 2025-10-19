import React, { useState, useEffect, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faSearch, faUserPlus, faCopy, faCheck, faUsers } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import config from '../config/api';
import './InvitedUsers.css';

const InvitedUsers = () => {
  const navigate = useNavigate();
  const { playerId } = useContext(BingoContext);
  const { t } = useTranslation();
  
  const [invitedUsers, setInvitedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalUsers, setTotalUsers] = useState(0);
  const [referralCode, setReferralCode] = useState('');
  const [referralLink, setReferralLink] = useState('');
  const [summary, setSummary] = useState({
    totalInvited: 0,
    activeUsers: 0,
    totalEarnings: 0,
    pendingEarnings: 0
  });
  const [copied, setCopied] = useState(false);

  // Fetch invited users and referral info
  useEffect(() => {
    const fetchData = async () => {
      if (!playerId) {
        navigate('/');
        return;
      }

      try {
        setLoading(true);
        
        // Use the telegram_id endpoint instead of user_id/details
        const userResponse = await axios.get(`${config.API_BASE_URL.replace(/\/$/, '')}/users/${parseInt(playerId)}`);
        
        // Extract referral data from user response
        const userData = userResponse.data;
        
        // Set referral info
        setSummary({
          totalInvited: 0, // This endpoint doesn't provide referral count
          activeUsers: 0, // This endpoint doesn't provide active user count
          totalEarnings: userData.total_referral_earnings || 0,
          referralCode: userData.username || 'N/A' // Use username as referral code for now
        });
        
        // Set referral code and link
        setReferralCode(userData.username || 'N/A');
        setReferralLink(`${window.location.origin}?ref=${userData.username}`);
        
        // For now, show empty invited users list with a message
        setInvitedUsers([]);
        setTotalPages(1);
        setTotalUsers(0);
        
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(t('referrals.failedToLoadReferralData'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [playerId, navigate, currentPage, searchTerm]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Handle back navigation
  const handleBack = () => {
    navigate(-1);
  };

  // Copy referral link
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(referralLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  // Copy referral code
  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(referralCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Get user status info
  const getUserStatusInfo = (status) => {
    switch (status) {
      case 'active':
        return { color: '#4CAF50', label: t('referrals.active') };
      case 'inactive':
        return { color: '#f44336', label: t('referrals.inactive') };
      case 'pending':
        return { color: '#ff9800', label: t('referrals.pending') };
      default:
        return { color: '#666', label: t('referrals.unknown') };
    }
  };

  if (loading) {
    return (
      <div className="invited-users-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>{t('referrals.loadingInvitedUsers')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="invited-users-container">
      {/* Header */}
      <div className="invited-users-header">
        <button className="back-button" onClick={handleBack}>
          <FontAwesomeIcon icon={faArrowLeft} />
        </button>
        <h1 className="invited-users-title">{t('referrals.invitedUsers')}</h1>
        <div className="header-actions">
          <button className="action-btn invite-btn">
            <FontAwesomeIcon icon={faUserPlus} />
            {t('referrals.invite')}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Referral Section */}
      <div className="referral-section">
        <div className="referral-card">
          <div className="referral-header">
            <h3>{t('referrals.yourReferralCode')}</h3>
            <button 
              className="copy-btn" 
              onClick={handleCopyCode}
              title={t('referrals.copyReferralCode')}
            >
              <FontAwesomeIcon icon={copied ? faCheck : faCopy} />
            </button>
          </div>
          <div className="referral-code-display">
            {referralCode}
          </div>
        </div>
        
        <div className="referral-card">
          <div className="referral-header">
            <h3>{t('referrals.yourReferralLink')}</h3>
            <button 
              className="copy-btn" 
              onClick={handleCopyLink}
              title={t('referrals.copyReferralLink')}
            >
              <FontAwesomeIcon icon={copied ? faCheck : faCopy} />
            </button>
          </div>
          <div className="referral-link-display">
            {referralLink}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="summary-section">
        <div className="summary-card">
          <div className="summary-icon total">👥</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalInvited}</div>
            <div className="summary-label">{t('referrals.totalInvited')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon active">✅</div>
          <div className="summary-content">
            <div className="summary-value">{summary.activeUsers}</div>
            <div className="summary-label">{t('referrals.activeUsers')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon earnings">💰</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalEarnings} ETB</div>
            <div className="summary-label">{t('referrals.totalEarnings')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon pending">⏳</div>
          <div className="summary-content">
            <div className="summary-value">{summary.pendingEarnings} ETB</div>
            <div className="summary-label">{t('referrals.pendingEarnings')}</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="search-section">
        <div className="search-box">
          <FontAwesomeIcon icon={faSearch} className="search-icon" />
          <input
            type="text"
            placeholder={t('referrals.searchInvitedUsers')}
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
      </div>

      {/* Invited Users List */}
      <div className="users-content">
        <div className="users-header-info">
          <h3>{t('referrals.invitedUsersCount', { count: totalUsers })}</h3>
        </div>
        
        {invitedUsers.length === 0 ? (
          <div className="no-users">
            <div className="no-users-icon">👥</div>
            <h3>{t('referrals.noInvitedUsersFound')}</h3>
            <p>{t('referrals.startInvitingFriends')}</p>
          </div>
        ) : (
          <div className="users-list">
            {invitedUsers.map((user) => {
              const statusInfo = getUserStatusInfo(user.status);
              
              return (
                <div key={user.id} className="user-item">
                  <div className="user-avatar">
                    <FontAwesomeIcon icon={faUsers} />
                  </div>
                  
                  <div className="user-details">
                    <div className="user-name">{user.username}</div>
                    <div className="user-info">
                      <span className="user-email">{user.email}</span>
                      <span className="user-separator">•</span>
                      <span className="user-date">{t('referrals.joined')} {formatDate(user.created_at)}</span>
                    </div>
                    <div className="user-stats">
                      <span className="user-balance">{t('referrals.balance')}: {user.balance} ETB</span>
                      <span className="user-separator">•</span>
                      <span className="user-games">{t('referrals.games')}: {user.total_games}</span>
                    </div>
                  </div>
                  
                  <div className="user-status">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: statusInfo.color }}
                    >
                      {statusInfo.label}
                    </span>
                    <div className="user-earnings">
                      {t('referrals.earned')}: {user.referral_earnings || 0} ETB
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="page-btn"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            {t('referrals.previous')}
          </button>
          
          <div className="page-numbers">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  className={`page-btn ${currentPage === pageNum ? 'active' : ''}`}
                  onClick={() => handlePageChange(pageNum)}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            className="page-btn"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            {t('referrals.next')}
          </button>
        </div>
      )}

      {/* Copy Success Message */}
      {copied && (
        <div className="copy-success">
          <FontAwesomeIcon icon={faCheck} />
          {t('referrals.copiedToClipboard')}
        </div>
      )}
    </div>
  );
};

export default InvitedUsers;
