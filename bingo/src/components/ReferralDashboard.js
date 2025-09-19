import React, { useState, useEffect } from 'react';
import './ReferralDashboard.css';
import referralApi from '../services/referralApi';
import WithdrawalRequest from './WithdrawalRequest';

const ReferralDashboard = () => {
  const [stats, setStats] = useState({
    total_referrals: 0,
    total_second_gen: 0,
    total_earnings: 0,
    pending_bonuses: 0,
    games_played_today: 0,
    games_played_this_week: 0,
    can_withdraw: false,
    referral_code: ''
  });
  const [bonuses, setBonuses] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showWithdrawalModal, setShowWithdrawalModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchReferralData();
  }, []);

  const fetchReferralData = async () => {
    try {
      setLoading(true);
      const [statsData, bonusesData, withdrawalsData, announcementsData] = await Promise.all([
        referralApi.getStats(),
        referralApi.getBonuses(),
        referralApi.getWithdrawals(),
        referralApi.getAnnouncements()
      ]);

      setStats(statsData);
      setBonuses(bonusesData);
      setWithdrawals(withdrawalsData);
      setAnnouncements(announcementsData);

    } catch (err) {
      setError('Failed to load referral data');
      console.error('Error fetching referral data:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyReferralCode = () => {
    navigator.clipboard.writeText(stats.referral_code);
    alert('Referral code copied to clipboard!');
  };

  if (loading) {
    return <div className="referral-loading">Loading referral data...</div>;
  }

  return (
    <div className="referral-dashboard">
      <div className="referral-header">
        <h2>🎯 Referral Dashboard</h2>
        <div className="referral-code-section">
          <label>Your Referral Code:</label>
          <div className="referral-code-display">
            <span className="referral-code">{stats.referral_code}</span>
            <button onClick={copyReferralCode} className="copy-btn">📋 Copy</button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'withdrawals' ? 'active' : ''}`}
          onClick={() => setActiveTab('withdrawals')}
        >
          💸 Withdrawals
        </button>
        <button 
          className={`tab-btn ${activeTab === 'bonuses' ? 'active' : ''}`}
          onClick={() => setActiveTab('bonuses')}
        >
          🎁 Bonuses
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <>
          {announcements.length > 0 && (
            <div className="announcements-section">
              <h3>📢 Announcements</h3>
              {announcements.map(announcement => (
                <div key={announcement.id} className="announcement-card">
                  <h4>{announcement.title}</h4>
                  <p>{announcement.message}</p>
                </div>
              ))}
            </div>
          )}

          <div className="stats-grid">
            <div className="stat-card">
              <h3>👥 Total Referrals</h3>
              <div className="stat-value">{stats.total_referrals}</div>
              <div className="stat-subtitle">First Generation</div>
            </div>

            <div className="stat-card">
              <h3>👥 Second Generation</h3>
              <div className="stat-value">{stats.total_second_gen}</div>
              <div className="stat-subtitle">Referred by your referrals</div>
            </div>

            <div className="stat-card">
              <h3>💰 Total Earnings</h3>
              <div className="stat-value">{stats.total_earnings.toFixed(2)} ETB</div>
              <div className="stat-subtitle">From referral bonuses</div>
            </div>

            <div className="stat-card">
              <h3>⏳ Pending Bonuses</h3>
              <div className="stat-value">{stats.pending_bonuses.toFixed(2)} ETB</div>
              <div className="stat-subtitle">Awaiting approval</div>
            </div>

            <div className="stat-card">
              <h3>🎮 Games Today</h3>
              <div className="stat-value">{stats.games_played_today}/3</div>
              <div className="stat-subtitle">Required: 3 per day</div>
            </div>

            <div className="stat-card">
              <h3>📅 Games This Week</h3>
              <div className="stat-value">{stats.games_played_this_week}/27</div>
              <div className="stat-subtitle">Required: 27 per week</div>
            </div>
          </div>

          <div className="withdrawal-section">
            <h3>💸 Withdrawal</h3>
            <div className="withdrawal-status">
              {stats.can_withdraw ? (
                <div className="withdrawal-eligible">
                  ✅ You are eligible for withdrawal (min 500 ETB)
                  <button 
                    className="withdrawal-request-btn"
                    onClick={() => setShowWithdrawalModal(true)}
                  >
                    Request Withdrawal
                  </button>
                </div>
              ) : (
                <div className="withdrawal-not-eligible">
                  ❌ Not eligible for withdrawal
                  <ul>
                    <li>Minimum 500 ETB required</li>
                    <li>Must play 3 games today</li>
                    <li>Must play 27 games this week</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {activeTab === 'withdrawals' && (
        <div className="withdrawals-management">
          <div className="withdrawal-header">
            <h3>💸 Withdrawal Management</h3>
            <button 
              className="new-withdrawal-btn"
              onClick={() => setShowWithdrawalModal(true)}
              disabled={!stats.can_withdraw}
            >
              + New Withdrawal
            </button>
          </div>

          <div className="withdrawal-stats">
            <div className="withdrawal-stat-card">
              <h4>Total Earnings</h4>
              <div className="stat-value">{stats.total_earnings.toFixed(2)} ETB</div>
            </div>
            <div className="withdrawal-stat-card">
              <h4>Eligible Amount</h4>
              <div className="stat-value">
                {stats.can_withdraw ? stats.total_earnings.toFixed(2) : '0.00'} ETB
              </div>
            </div>
            <div className="withdrawal-stat-card">
              <h4>Min Withdrawal</h4>
              <div className="stat-value">500.00 ETB</div>
            </div>
          </div>

          <div className="withdrawal-requirements">
            <h4>📋 Withdrawal Requirements</h4>
            <div className="requirements-list">
              <div className={`requirement ${stats.total_earnings >= 500 ? 'met' : 'not-met'}`}>
                <span className="requirement-icon">
                  {stats.total_earnings >= 500 ? '✅' : '❌'}
                </span>
                <span>Minimum 500 ETB earnings: {stats.total_earnings.toFixed(2)} ETB</span>
              </div>
              <div className={`requirement ${stats.games_played_today >= 3 ? 'met' : 'not-met'}`}>
                <span className="requirement-icon">
                  {stats.games_played_today >= 3 ? '✅' : '❌'}
                </span>
                <span>Play 3 games today: {stats.games_played_today}/3</span>
              </div>
              <div className={`requirement ${stats.games_played_this_week >= 27 ? 'met' : 'not-met'}`}>
                <span className="requirement-icon">
                  {stats.games_played_this_week >= 27 ? '✅' : '❌'}
                </span>
                <span>Play 27 games this week: {stats.games_played_this_week}/27</span>
              </div>
            </div>
          </div>

          <div className="withdrawals-history">
            <h4>📜 Withdrawal History</h4>
            <div className="withdrawals-list">
              {withdrawals.length > 0 ? (
                withdrawals.map(withdrawal => (
                  <div key={withdrawal.id} className="withdrawal-item-detailed">
                    <div className="withdrawal-main-info">
                      <div className="withdrawal-amount">{withdrawal.amount} ETB</div>
                      <div className={`withdrawal-status ${withdrawal.status}`}>
                        {withdrawal.status.toUpperCase()}
                      </div>
                    </div>
                    <div className="withdrawal-details">
                      <div className="withdrawal-date">
                        <strong>Requested:</strong> {new Date(withdrawal.created_at).toLocaleDateString()}
                      </div>
                      {withdrawal.processed_at && (
                        <div className="withdrawal-processed">
                          <strong>Processed:</strong> {new Date(withdrawal.processed_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-withdrawals">No withdrawal requests yet</div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'bonuses' && (
        <div className="bonuses-management">
          <h3>🎁 Bonus Management</h3>
          <div className="bonuses-list">
            {bonuses.length > 0 ? (
              bonuses.map(bonus => (
                <div key={bonus.id} className="bonus-item-detailed">
                  <div className="bonus-main-info">
                    <div className="bonus-type">{bonus.bonus_type}</div>
                    <div className="bonus-amount">+{bonus.bonus_amount} ETB</div>
                  </div>
                  <div className="bonus-details">
                    <div className="bonus-winner">From: {bonus.winner}</div>
                    <div className="bonus-date">
                      {new Date(bonus.created_at).toLocaleDateString()}
                    </div>
                    <div className={`bonus-status ${bonus.status}`}>
                      {bonus.status.toUpperCase()}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-bonuses">No bonuses yet</div>
            )}
          </div>
        </div>
      )}

      {/* Withdrawal Modal */}
      {showWithdrawalModal && (
        <WithdrawalRequest onClose={() => setShowWithdrawalModal(false)} />
      )}
    </div>
  );
};

export default ReferralDashboard;
