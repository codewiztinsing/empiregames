import React, { useState, useEffect, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faUser, faEdit, faSave, faTimes } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import config from '../config/api';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const { playerId, playerName, setPlayerName } = useContext(BingoContext);
  const { t } = useTranslation();
  
  const [profile, setProfile] = useState({
    id: null,
    username: '',
    email: '',
    phone: '',
    balance: 0,
    totalGames: 0,
    totalWins: 0,
    totalEarnings: 0,
    joinDate: '',
    lastLogin: '',
    referralCode: '',
    invitedBy: '',
    invitedUsers: 0
  });
  
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch profile data
  useEffect(() => {
    const fetchProfile = async () => {
      if (!playerId) {
        navigate('/');
        return;
      }

      try {
        setLoading(true);
        const response = await axios.get(`${config.API_BASE_URL.replace(/\/$/, '')}/users/${parseInt(playerId)}`);
        
        // Transform the response data to match expected profile structure
        const userData = response.data;
        const transformedProfile = {
          id: userData.id,
          username: userData.username,
          email: userData.email,
          phone: userData.phone,
          telegram_id: userData.telegram_id,
          balance: 0, // Not provided by this endpoint
          totalGames: userData.games_played_this_week || 0,
          totalWins: 0, // Not provided by this endpoint
          totalEarnings: userData.total_referral_earnings || 0,
          referralCode: userData.username, // Use username as referral code
          invitedBy: 'Unknown', // Not provided by this endpoint
          invitedUsers: 0, // Not provided by this endpoint
          joinDate: 'Unknown', // Not provided by this endpoint
          lastLogin: 'Unknown' // Not provided by this endpoint
        };
        
        setProfile(transformedProfile);
      } catch (error) {
        console.error('Error fetching profile:', error);
        setError(t('profile.failedToLoadProfile'));
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [playerId, navigate]);

  // Handle profile update
  const handleUpdate = async () => {
    try {
      setSaving(true);
      setError('');
      
      const updateData = {
        username: profile.username,
        email: profile.email,
        phone: profile.phone
      };

      await axios.put(`${config.API_BASE_URL.replace(/\/$/, '')}/users/${parseInt(playerId)}`, updateData);
      
      setPlayerName(profile.username);
      setSuccess(t('profile.profileUpdated'));
      setIsEditing(false);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError(t('profile.failedToUpdateProfile'));
    } finally {
      setSaving(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle back navigation
  const handleBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="profile-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>{t('profile.loadingProfile')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      {/* Header */}
      <div className="profile-header">
        <button className="back-button" onClick={handleBack}>
          <FontAwesomeIcon icon={faArrowLeft} />
        </button>
        <h1 className="profile-title">{t('profile.profile')}</h1>
        <div className="profile-actions">
          {isEditing ? (
            <>
              <button 
                className="action-btn save-btn" 
                onClick={handleUpdate}
                disabled={saving}
              >
                <FontAwesomeIcon icon={faSave} />
                {saving ? t('profile.saving') : t('profile.save')}
              </button>
              <button 
                className="action-btn cancel-btn" 
                onClick={() => setIsEditing(false)}
                disabled={saving}
              >
                <FontAwesomeIcon icon={faTimes} />
                {t('profile.cancel')}
              </button>
            </>
          ) : (
            <button 
              className="action-btn edit-btn" 
              onClick={() => setIsEditing(true)}
            >
              <FontAwesomeIcon icon={faEdit} />
              {t('profile.edit')}
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error-message">
          {error}
        </div>
      )}
      {success && (
        <div className="message success-message">
          {success}
        </div>
      )}

      {/* Profile Content */}
      <div className="profile-content">
        {/* Profile Picture Section */}
        <div className="profile-picture-section">
          <div className="profile-picture">
            <FontAwesomeIcon icon={faUser} />
          </div>
          <div className="profile-info">
            <h2 className="profile-name">{profile.username || t('profile.user')}</h2>
            <p className="profile-id">ID: {profile.id}</p>
          </div>
        </div>

        {/* Profile Details */}
        <div className="profile-details">
          <div className="detail-section">
            <h3 className="section-title">{t('profile.personalInfo')}</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>{t('profile.username')}</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profile.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.username || t('profile.notSet')}</span>
                )}
              </div>
              
              <div className="detail-item">
                <label>{t('profile.email')}</label>
                {isEditing ? (
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.email || t('profile.notSet')}</span>
                )}
              </div>
              
              <div className="detail-item">
                <label>{t('profile.phone')}</label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.phone || t('profile.notSet')}</span>
                )}
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">{t('profile.accountStatistics')}</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.balance} ETB</div>
                  <div className="stat-label">{t('profile.currentBalance')}</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🎮</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalGames}</div>
                  <div className="stat-label">{t('profile.totalGames')}</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🏆</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalWins}</div>
                  <div className="stat-label">{t('profile.totalWins')}</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">💎</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalEarnings} ETB</div>
                  <div className="stat-label">{t('profile.totalEarnings')}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">{t('profile.referralInformation')}</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>{t('profile.referralCode')}</label>
                <span className="detail-value referral-code">{profile.referralCode}</span>
              </div>
              
              <div className="detail-item">
                <label>{t('profile.invitedBy')}</label>
                <span className="detail-value">{profile.invitedBy || t('profile.noOne')}</span>
              </div>
              
              <div className="detail-item">
                <label>{t('profile.invitedUsers')}</label>
                <span className="detail-value">{profile.invitedUsers}</span>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">{t('profile.accountInformation')}</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>{t('profile.joinDate')}</label>
                <span className="detail-value">{profile.joinDate || t('profile.unknown')}</span>
              </div>
              
              <div className="detail-item">
                <label>{t('profile.lastLogin')}</label>
                <span className="detail-value">{profile.lastLogin || t('profile.unknown')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
