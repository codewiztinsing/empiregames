import React, { useState } from 'react';
import './ReferralCodeInput.css';
import referralApi from '../services/referralApi';

const ReferralCodeInput = ({ onReferralSet, onSkip }) => {
  const [referralCode, setReferralCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!referralCode.trim()) {
      setError('Please enter a referral code');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await referralApi.setReferrer(referralCode.trim());

      if (data.success) {
        setSuccess(data.message);
        setTimeout(() => {
          onReferralSet && onReferralSet();
        }, 1500);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to set referral code. Please try again.');
      console.error('Error setting referral code:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    onSkip && onSkip();
  };

  return (
    <div className="referral-code-input">
      <div className="referral-header">
        <h2>🎯 Join with Referral Code</h2>
        <p>Enter a referral code to join under a sponsor, or skip to become an agent under Aker Bingo</p>
      </div>

      <div className="referral-benefits">
        <h3>💰 Referral Benefits</h3>
        <div className="benefits-grid">
          <div className="benefit-item">
            <div className="benefit-icon">🎮</div>
            <div className="benefit-text">
              <strong>4% First Generation</strong>
              <span>Earn 4% when your referrals win</span>
            </div>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">👥</div>
            <div className="benefit-text">
              <strong>1% Second Generation</strong>
              <span>Earn 1% from your referrals' referrals</span>
            </div>
          </div>
          <div className="benefit-item">
            <div className="benefit-icon">🏆</div>
            <div className="benefit-text">
              <strong>Weekly Withdrawals</strong>
              <span>Withdraw earnings weekly (min 500 ETB)</span>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="referral-form">
        <div className="form-group">
          <label htmlFor="referralCode">Referral Code</label>
          <input
            type="text"
            id="referralCode"
            value={referralCode}
            onChange={(e) => setReferralCode(e.target.value.toUpperCase())}
            placeholder="Enter referral code here..."
            className="referral-input"
            disabled={loading}
            maxLength={15}
          />
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

        <div className="form-actions">
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !referralCode.trim()}
          >
            {loading ? '⏳ Setting...' : '✅ Join with Code'}
          </button>
          
          <button
            type="button"
            onClick={handleSkip}
            className="skip-btn"
            disabled={loading}
          >
            🚀 Skip (Become Agent)
          </button>
        </div>
      </form>

      <div className="referral-info">
        <h4>ℹ️ Important Notes</h4>
        <ul>
          <li>You can only change your sponsor once</li>
          <li>If you skip, you'll be an agent under Aker Bingo</li>
          <li>Agents earn 3% inhouse bonus from all wins</li>
          <li>Minimum withdrawal amount is 500 ETB</li>
          <li>Must play 3 games daily and 27 games weekly to withdraw</li>
        </ul>
      </div>
    </div>
  );
};

export default ReferralCodeInput;
