import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ReferralLanding.css';
import referralApi from '../services/referralApi';

const ReferralLanding = () => {
  const [showReferralSetup, setShowReferralSetup] = useState(false);
  const [playerId, setPlayerId] = useState('');
  const [roomId, setRoomId] = useState('');
  const [playerName, setPlayerName] = useState('');
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkUserStatus();
    // Get query parameters
    const queryParams = new URLSearchParams(window.location.search);
    const urlPlayerId = queryParams.get('playerId');
    const urlRoomId = queryParams.get('betAmount');
    const urlPlayerName = queryParams.get('playerName');
    
    if (urlPlayerId) setPlayerId(urlPlayerId);
    if (urlRoomId) setRoomId(urlRoomId);
    if (urlPlayerName) setPlayerName(urlPlayerName);

  }, []);

  const checkUserStatus = async () => {
    try {
    
      setLoading(true);
      const stats = await referralApi.getStats();
      setUserStats(stats);
    
      // If user has no referrer and hasn't changed sponsor, show setup
      if (!stats.referred_by && !stats.sponsor_changed) {
        setShowReferralSetup(true);
      }
    } catch (error) {
      console.error('Error checking user status:', error);
      // If API fails, assume new user
      setShowReferralSetup(true);
    } finally {
      setLoading(false);
    }
  };

  const handleReferralSet = () => {
    setShowReferralSetup(false);
    navigate('/selection');
  };

  const handleSkip = () => {
    setShowReferralSetup(false);
    console.log('playerId', playerId);
    console.log('roomId', roomId);
    console.log('playerName', playerName);
    const url = `/selection?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`
    navigate(url);
  };

  if (loading) {
    return (
      <div className="referral-landing-loading">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (showReferralSetup) {
    return (
      <div className="referral-landing">
        <div className="referral-landing-content">
          <h1>🎯 Welcome to Bingo Referral System!</h1>
          <p>Join our referral program and start earning bonuses from your referrals' wins!</p>
          
          <div className="referral-benefits-preview">
            <h3>💰 How It Works</h3>
            <div className="benefits-grid">
              <div className="benefit-card">
                <div className="benefit-icon">🎮</div>
                <h4>4% First Generation</h4>
                <p>Earn 4% when your direct referrals win</p>
              </div>
              <div className="benefit-card">
                <div className="benefit-icon">👥</div>
                <h4>1% Second Generation</h4>
                <p>Earn 1% from your referrals' referrals</p>
              </div>
              <div className="benefit-card">
                <div className="benefit-icon">🏆</div>
                <h4>Weekly Withdrawals</h4>
                <p>Withdraw earnings weekly (min 500 ETB)</p>
              </div>
            </div>
          </div>

          <div className="referral-options">
            <button 
              className="setup-referral-btn"
              onClick={() => navigate('/referral-setup')}
            >
              🔗 Setup Referral Code
            </button>
            <button 
              className="skip-btn"
              onClick={handleSkip}
            >
              🚀 Skip (Become Agent)
            </button>
          </div>

          <div className="referral-info">
            <p><strong>Note:</strong> You can only change your sponsor once. If you skip, you'll be an agent under Aker Bingo and earn 3% inhouse bonus from all wins.</p>
          </div>
        </div>
      </div>
    );
  }

  // User already has referral setup, show dashboard
  return (
    <div className="referral-landing">
      <div className="referral-landing-content">
        <h1>🎯 Referral Dashboard</h1>
        <p>Welcome back! Manage your referral earnings and statistics.</p>
        
        <div className="referral-actions">
          <button 
            className="dashboard-btn"
            onClick={() => navigate('/referrals')}
          >
            📊 View Dashboard
          </button>
          <button 
            className="play-btn"
            onClick={() => navigate('/selection')}
          >
            🎮 Play Bingo
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReferralLanding;
