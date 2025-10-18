import React, { useState, useEffect, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faSearch, faUserPlus, faCopy, faCheck, faUsers } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import axios from 'axios';
import config from '../config/api';
import './InvitedUsers.css';

const InvitedUsers = () => {
  const navigate = useNavigate();
  const { playerId } = useContext(BingoContext);
  
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
        setError('Failed to load referral data');
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
        return { color: '#4CAF50', label: 'Active' };
      case 'inactive':
        return { color: '#f44336', label: 'Inactive' };
      case 'pending':
        return { color: '#ff9800', label: 'Pending' };
      default:
        return { color: '#666', label: 'Unknown' };
    }
  };

  if (loading) {
    return (
      <div className="invited-users-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading invited users...</p>
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
        <h1 className="invited-users-title">Invited Users</h1>
        <div className="header-actions">
          <button className="action-btn invite-btn">
            <FontAwesomeIcon icon={faUserPlus} />
            Invite
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
            <h3>Your Referral Code</h3>
            <button 
              className="copy-btn" 
              onClick={handleCopyCode}
              title="Copy referral code"
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
            <h3>Your Referral Link</h3>
            <button 
              className="copy-btn" 
              onClick={handleCopyLink}
              title="Copy referral link"
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
            <div className="summary-label">Total Invited</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon active">✅</div>
          <div className="summary-content">
            <div className="summary-value">{summary.activeUsers}</div>
            <div className="summary-label">Active Users</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon earnings">💰</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalEarnings} ETB</div>
            <div className="summary-label">Total Earnings</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon pending">⏳</div>
          <div className="summary-content">
            <div className="summary-value">{summary.pendingEarnings} ETB</div>
            <div className="summary-label">Pending Earnings</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="search-section">
        <div className="search-box">
          <FontAwesomeIcon icon={faSearch} className="search-icon" />
          <input
            type="text"
            placeholder="Search invited users..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
      </div>

      {/* Invited Users List */}
      <div className="users-content">
        <div className="users-header-info">
          <h3>Invited Users ({totalUsers})</h3>
        </div>
        
        {invitedUsers.length === 0 ? (
          <div className="no-users">
            <div className="no-users-icon">👥</div>
            <h3>No invited users found</h3>
            <p>Start inviting friends to earn referral bonuses!</p>
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
                      <span className="user-date">Joined {formatDate(user.created_at)}</span>
                    </div>
                    <div className="user-stats">
                      <span className="user-balance">Balance: {user.balance} ETB</span>
                      <span className="user-separator">•</span>
                      <span className="user-games">Games: {user.total_games}</span>
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
                      Earned: {user.referral_earnings || 0} ETB
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
            Previous
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
            Next
          </button>
        </div>
      )}

      {/* Copy Success Message */}
      {copied && (
        <div className="copy-success">
          <FontAwesomeIcon icon={faCheck} />
          Copied to clipboard!
        </div>
      )}
    </div>
  );
};

export default InvitedUsers;
