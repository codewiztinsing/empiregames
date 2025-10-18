import React, { useState, useEffect, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faUser, faEdit, faSave, faTimes } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import axios from 'axios';
import config from '../config/api';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const { playerId, playerName, setPlayerName } = useContext(BingoContext);
  
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
        const response = await axios.get(`${config.API_BASE_URL.replace(/\/$/, '')}/users/${parseInt(playerId)}/details/`);
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        setError('Failed to load profile data');
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
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile');
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
          <p>Loading profile...</p>
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
        <h1 className="profile-title">Profile</h1>
        <div className="profile-actions">
          {isEditing ? (
            <>
              <button 
                className="action-btn save-btn" 
                onClick={handleUpdate}
                disabled={saving}
              >
                <FontAwesomeIcon icon={faSave} />
                {saving ? 'Saving...' : 'Save'}
              </button>
              <button 
                className="action-btn cancel-btn" 
                onClick={() => setIsEditing(false)}
                disabled={saving}
              >
                <FontAwesomeIcon icon={faTimes} />
                Cancel
              </button>
            </>
          ) : (
            <button 
              className="action-btn edit-btn" 
              onClick={() => setIsEditing(true)}
            >
              <FontAwesomeIcon icon={faEdit} />
              Edit
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
            <h2 className="profile-name">{profile.username || 'User'}</h2>
            <p className="profile-id">ID: {profile.id}</p>
          </div>
        </div>

        {/* Profile Details */}
        <div className="profile-details">
          <div className="detail-section">
            <h3 className="section-title">Personal Information</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Username</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={profile.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.username || 'Not set'}</span>
                )}
              </div>
              
              <div className="detail-item">
                <label>Email</label>
                {isEditing ? (
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.email || 'Not set'}</span>
                )}
              </div>
              
              <div className="detail-item">
                <label>Phone</label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={profile.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="edit-input"
                  />
                ) : (
                  <span className="detail-value">{profile.phone || 'Not set'}</span>
                )}
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">Account Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.balance} ETB</div>
                  <div className="stat-label">Current Balance</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🎮</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalGames}</div>
                  <div className="stat-label">Total Games</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">🏆</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalWins}</div>
                  <div className="stat-label">Total Wins</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon">💎</div>
                <div className="stat-content">
                  <div className="stat-value">{profile.totalEarnings} ETB</div>
                  <div className="stat-label">Total Earnings</div>
                </div>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">Referral Information</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Referral Code</label>
                <span className="detail-value referral-code">{profile.referralCode}</span>
              </div>
              
              <div className="detail-item">
                <label>Invited By</label>
                <span className="detail-value">{profile.invitedBy || 'No one'}</span>
              </div>
              
              <div className="detail-item">
                <label>Invited Users</label>
                <span className="detail-value">{profile.invitedUsers}</span>
              </div>
            </div>
          </div>

          <div className="detail-section">
            <h3 className="section-title">Account Information</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Join Date</label>
                <span className="detail-value">{profile.joinDate || 'Unknown'}</span>
              </div>
              
              <div className="detail-item">
                <label>Last Login</label>
                <span className="detail-value">{profile.lastLogin || 'Unknown'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
