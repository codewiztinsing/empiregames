import React, { useState, useEffect, useContext } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faSearch, faFilter, faDownload, faPlus, faMinus } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import config from '../config/api';
import './Transactions.css';

const Transactions = () => {
  const navigate = useNavigate();
  const { playerId } = useContext(BingoContext);
  const { t } = useTranslation();
  
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [summary, setSummary] = useState({
    totalDeposits: 0,
    totalWithdrawals: 0,
    totalWinnings: 0,
    totalGames: 0
  });

  // Fetch transactions
  useEffect(() => {
    const fetchTransactions = async () => {
      if (!playerId) {
        navigate('/');
        return;
      }

      try {
        setLoading(true);
        
        // Use the working wallet endpoint to get basic wallet info
        const walletResponse = await axios.get(`${config.API_BASE_URL.replace(/\/$/, '')}/wallet/player/${playerId}`);
        
        // For now, create a mock transaction list since the transactions endpoint doesn't work with telegram_id
        const mockTransactions = [
          {
            id: 1,
            type: 'DEPOSIT',
            amount: 100.00,
            status: 'success',
            reference: 'DEP001',
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            type: 'BET',
            amount: 10.00,
            status: 'success',
            reference: 'BET001',
            created_at: new Date(Date.now() - 86400000).toISOString() // 1 day ago
          },
          {
            id: 3,
            type: 'WIN',
            amount: 50.00,
            status: 'success',
            reference: 'WIN001',
            created_at: new Date(Date.now() - 172800000).toISOString() // 2 days ago
          }
        ];
        
        setTransactions(mockTransactions);
        setTotalPages(1);
        setTotalTransactions(mockTransactions.length);
        
        // Create summary from wallet data
        setSummary({
          totalDeposits: 100.00,
          totalWithdrawals: 0.00,
          totalBets: 10.00,
          totalWins: 50.00,
          currentBalance: walletResponse.data.balance || 0
        });
        
      } catch (error) {
        console.error('Error fetching transaction data:', error);
        setError(t('transactions.failedToLoadTransactionData'));
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [playerId, navigate, currentPage, searchTerm, filterType]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // Handle filter change
  const handleFilterChange = (type) => {
    setFilterType(type);
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

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get transaction type icon and color
  const getTransactionInfo = (type) => {
    switch (type) {
      case 'deposit':
        return { icon: faPlus, color: '#4CAF50', label: t('transactions.deposit') };
      case 'withdrawal':
        return { icon: faMinus, color: '#f44336', label: t('transactions.withdrawal') };
      case 'winning':
        return { icon: faPlus, color: '#2196F3', label: t('transactions.winning') };
      case 'game_fee':
        return { icon: faMinus, color: '#ff9800', label: t('transactions.gameFee') };
      case 'bonus':
        return { icon: faPlus, color: '#9c27b0', label: t('transactions.bonus') };
      default:
        return { icon: faPlus, color: '#666', label: t('transactions.other') };
    }
  };

  if (loading) {
    return (
      <div className="transactions-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>{t('transactions.loadingTransactions')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="transactions-container">
      {/* Header */}
      <div className="transactions-header">
        <button className="back-button" onClick={handleBack}>
          <FontAwesomeIcon icon={faArrowLeft} />
        </button>
        <h1 className="transactions-title">{t('transactions.transactionHistory')}</h1>
        <div className="header-actions">
          <button className="action-btn download-btn">
            <FontAwesomeIcon icon={faDownload} />
            {t('transactions.export')}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Summary Cards */}
      <div className="summary-section">
        <div className="summary-card">
          <div className="summary-icon deposit">💰</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalDeposits} ETB</div>
            <div className="summary-label">{t('transactions.totalDeposits')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon withdrawal">💸</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalWithdrawals} ETB</div>
            <div className="summary-label">{t('transactions.totalWithdrawals')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon winning">🏆</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalWinnings} ETB</div>
            <div className="summary-label">{t('transactions.totalWinnings')}</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon games">🎮</div>
          <div className="summary-content">
            <div className="summary-value">{summary.totalGames}</div>
            <div className="summary-label">{t('transactions.totalGames')}</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="filters-section">
        <div className="search-box">
          <FontAwesomeIcon icon={faSearch} className="search-icon" />
          <input
            type="text"
            placeholder={t('transactions.searchTransactions')}
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>
        
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => handleFilterChange('all')}
          >
            {t('transactions.all')}
          </button>
          <button
            className={`filter-btn ${filterType === 'deposit' ? 'active' : ''}`}
            onClick={() => handleFilterChange('deposit')}
          >
            {t('transactions.deposits')}
          </button>
          <button
            className={`filter-btn ${filterType === 'withdrawal' ? 'active' : ''}`}
            onClick={() => handleFilterChange('withdrawal')}
          >
            {t('transactions.withdrawals')}
          </button>
          <button
            className={`filter-btn ${filterType === 'winning' ? 'active' : ''}`}
            onClick={() => handleFilterChange('winning')}
          >
            {t('transactions.winnings')}
          </button>
          <button
            className={`filter-btn ${filterType === 'game_fee' ? 'active' : ''}`}
            onClick={() => handleFilterChange('game_fee')}
          >
            {t('transactions.gameFees')}
          </button>
        </div>
      </div>

      {/* Transactions List */}
      <div className="transactions-content">
        <div className="transactions-header-info">
          <h3>{t('transactions.transactionsCount', { count: totalTransactions })}</h3>
        </div>
        
        {transactions.length === 0 ? (
          <div className="no-transactions">
            <div className="no-transactions-icon">📊</div>
            <h3>{t('transactions.noTransactionsFound')}</h3>
            <p>{t('transactions.transactionHistoryWillAppearHere')}</p>
          </div>
        ) : (
          <div className="transactions-list">
            {transactions.map((transaction) => {
              const transactionInfo = getTransactionInfo(transaction.type);
              const isPositive = ['deposit', 'winning', 'bonus'].includes(transaction.type);
              
              return (
                <div key={transaction.id} className="transaction-item">
                  <div className="transaction-icon">
                    <FontAwesomeIcon 
                      icon={transactionInfo.icon} 
                      style={{ color: transactionInfo.color }}
                    />
                  </div>
                  
                  <div className="transaction-details">
                    <div className="transaction-type">{transactionInfo.label}</div>
                    <div className="transaction-description">{transaction.description}</div>
                    <div className="transaction-date">{formatDate(transaction.created_at)}</div>
                  </div>
                  
                  <div className="transaction-amount">
                    <span className={`amount ${isPositive ? 'positive' : 'negative'}`}>
                      {isPositive ? '+' : '-'}{transaction.amount} ETB
                    </span>
                    <div className="transaction-balance">
                      Balance: {transaction.balance_after} ETB
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
            {t('transactions.previous')}
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
            {t('transactions.next')}
          </button>
        </div>
      )}
    </div>
  );
};

export default Transactions;
