import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTelegramAuth } from '../hooks/useTelegramAuth';

const UserProfile = ({ onLogout }) => {
  const { 
    user, 
    getUserWallet, 
    getUserTransactions, 
    checkDepositStatus,
    refreshUser 
  } = useAuth();
  
  const { handleLogout, showConfirm } = useTelegramAuth();
  
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState(null);
  const [hasDeposit, setHasDeposit] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUserData = async () => {
      if (!user) return;

      try {
        setIsLoading(true);
        
        // Load wallet data
        const walletData = await getUserWallet();
        setWallet(walletData);

        // Load recent transactions
        const transactionsData = await getUserTransactions(5);
        setTransactions(transactionsData);

        // Check deposit status
        const depositStatus = await checkDepositStatus();
        setHasDeposit(depositStatus);

        // Refresh user data
        await refreshUser();
      } catch (error) {
        console.error('Failed to load user data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, [user, getUserWallet, getUserTransactions, checkDepositStatus, refreshUser]);

  const handleLogoutClick = () => {
    showConfirm(
      'Are you sure you want to logout?',
      async (confirmed) => {
        if (confirmed) {
          await handleLogout();
          if (onLogout) {
            onLogout();
          }
        }
      }
    );
  };

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
        fontSize: '16px',
        color: '#666'
      }}>
        Loading profile...
      </div>
    );
  }

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '15px'
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            backgroundColor: '#007bff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            color: 'white',
            marginRight: '15px'
          }}>
            {user?.first_name?.charAt(0) || 'U'}
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '20px' }}>
              {user?.first_name} {user?.last_name}
            </h2>
            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
              @{user?.username}
            </p>
          </div>
        </div>

        {/* User Info */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '15px',
          marginBottom: '20px'
        }}>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Telegram ID</div>
            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{user?.telegram_id}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Phone</div>
            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
              {user?.phone || 'Not provided'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Referral Code</div>
            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{user?.referral_code}</div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>Status</div>
            <div style={{ 
              fontSize: '14px', 
              fontWeight: 'bold',
              color: hasDeposit ? '#28a745' : '#ffc107'
            }}>
              {hasDeposit ? 'Verified' : 'Pending'}
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={handleLogoutClick}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer',
            transition: 'background-color 0.3s ease'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#c82333'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#dc3545'}
        >
          Logout
        </button>
      </div>

      {/* Wallet Info */}
      {wallet && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '18px' }}>Wallet</h3>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '15px'
          }}>
            <span style={{ fontSize: '16px' }}>Balance</span>
            <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#28a745' }}>
              {wallet.wallet?.balance?.toFixed(2) || '0.00'} ETB
            </span>
          </div>
          
          {wallet.summary && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '10px',
              fontSize: '12px'
            }}>
              <div>
                <div style={{ color: '#666' }}>Total Deposits</div>
                <div style={{ fontWeight: 'bold' }}>{wallet.summary.total_deposits?.toFixed(2) || '0.00'}</div>
              </div>
              <div>
                <div style={{ color: '#666' }}>Total Wins</div>
                <div style={{ fontWeight: 'bold', color: '#28a745' }}>
                  {wallet.summary.total_wins?.toFixed(2) || '0.00'}
                </div>
              </div>
              <div>
                <div style={{ color: '#666' }}>Total Bets</div>
                <div style={{ fontWeight: 'bold', color: '#dc3545' }}>
                  {wallet.summary.total_bets?.toFixed(2) || '0.00'}
                </div>
              </div>
              <div>
                <div style={{ color: '#666' }}>Net Balance</div>
                <div style={{ 
                  fontWeight: 'bold',
                  color: wallet.summary.net_balance >= 0 ? '#28a745' : '#dc3545'
                }}>
                  {wallet.summary.net_balance?.toFixed(2) || '0.00'}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Transactions */}
      {transactions && transactions.transactions && transactions.transactions.length > 0 && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '18px' }}>Recent Transactions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {transactions.transactions.slice(0, 5).map((transaction, index) => (
              <div key={index} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                fontSize: '14px'
              }}>
                <div>
                  <div style={{ fontWeight: 'bold' }}>
                    {transaction.type}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div style={{
                  fontWeight: 'bold',
                  color: transaction.type === 'WIN' ? '#28a745' : 
                        transaction.type === 'DEPOSIT' ? '#28a745' : '#dc3545'
                }}>
                  {transaction.type === 'WIN' || transaction.type === 'DEPOSIT' ? '+' : '-'}
                  {transaction.amount?.toFixed(2)} ETB
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
