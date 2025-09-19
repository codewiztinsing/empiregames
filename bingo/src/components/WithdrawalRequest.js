import React, { useState, useEffect } from 'react';
import './WithdrawalRequest.css';
import referralApi from '../services/referralApi';

const WithdrawalRequest = ({ onClose }) => {
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await referralApi.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const withdrawalAmount = parseFloat(amount);
    
    if (!amount || isNaN(withdrawalAmount) || withdrawalAmount < 500) {
      setError('Minimum withdrawal amount is 500 ETB');
      return;
    }

    if (withdrawalAmount > stats.total_earnings) {
      setError('Insufficient referral earnings');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await referralApi.createWithdrawalRequest(withdrawalAmount);

      if (data.success) {
        setSuccess(data.message);
        setTimeout(() => {
          onClose && onClose();
        }, 2000);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to create withdrawal request. Please try again.');
      console.error('Error creating withdrawal request:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!stats) {
    return (
      <div className="withdrawal-loading">
        <div className="loading-spinner"></div>
        <p>Loading withdrawal information...</p>
      </div>
    );
  }

  return (
    <div className="withdrawal-request">
      <div className="withdrawal-header">
        <h2>💸 Request Withdrawal</h2>
        <button onClick={onClose} className="close-btn">✕</button>
      </div>

      <div className="withdrawal-stats">
        <div className="stat-item">
          <span className="stat-label">Total Earnings:</span>
          <span className="stat-value">{stats.total_earnings.toFixed(2)} ETB</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Games Today:</span>
          <span className="stat-value">{stats.games_played_today}/3</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Games This Week:</span>
          <span className="stat-value">{stats.games_played_this_week}/27</span>
        </div>
      </div>

      {!stats.can_withdraw && (
        <div className="withdrawal-requirements">
          <h3>⚠️ Requirements Not Met</h3>
          <ul>
            <li className={stats.total_earnings >= 500 ? 'met' : 'not-met'}>
              Minimum 500 ETB earnings: {stats.total_earnings.toFixed(2)} ETB
            </li>
            <li className={stats.games_played_today >= 3 ? 'met' : 'not-met'}>
              Play 3 games today: {stats.games_played_today}/3
            </li>
            <li className={stats.games_played_this_week >= 27 ? 'met' : 'not-met'}>
              Play 27 games this week: {stats.games_played_this_week}/27
            </li>
          </ul>
        </div>
      )}

      {stats.can_withdraw && (
        <form onSubmit={handleSubmit} className="withdrawal-form">
          <div className="form-group">
            <label htmlFor="amount">Withdrawal Amount (ETB)</label>
            <div className="amount-input-container">
              <input
                type="number"
                id="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="500.00"
                min="500"
                max={stats.total_earnings}
                step="0.01"
                className="amount-input"
                disabled={loading}
              />
              <span className="currency">ETB</span>
            </div>
            <div className="amount-hint">
              Min: 500 ETB | Max: {stats.total_earnings.toFixed(2)} ETB
            </div>
          </div>

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              ✅ {success}
            </div>
          )}

          <div className="withdrawal-info">
            <h4>ℹ️ Withdrawal Information</h4>
            <ul>
              <li>Withdrawals are processed weekly</li>
              <li>Minimum amount: 500 ETB</li>
              <li>You can only have one pending request at a time</li>
              <li>Processing time: 1-3 business days</li>
            </ul>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-btn"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="submit-btn"
              disabled={loading || !amount || parseFloat(amount) < 500}
            >
              {loading ? '⏳ Processing...' : '💸 Request Withdrawal'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default WithdrawalRequest;
