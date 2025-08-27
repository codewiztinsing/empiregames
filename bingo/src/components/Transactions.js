import React, { useState, useEffect } from 'react';
import { DollarSign, ArrowUp, ArrowDown, Calendar, Filter, Search } from 'lucide-react';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock transaction data - replace with actual API call
  useEffect(() => {
    const mockTransactions = [
      {
        id: 1,
        type: 'deposit',
        amount: 500.00,
        description: 'Mobile Money Deposit',
        date: '2025-01-20T10:30:00Z',
        status: 'completed',
        reference: 'TXN001234567'
      },
      {
        id: 2,
        type: 'withdrawal',
        amount: 150.00,
        description: 'Withdrawal to Bank Account',
        date: '2025-01-19T15:45:00Z',
        status: 'completed',
        reference: 'TXN001234568'
      },
      {
        id: 3,
        type: 'game_fee',
        amount: 25.00,
        description: 'Bingo Game Entry Fee',
        date: '2025-01-19T14:20:00Z',
        status: 'completed',
        reference: 'TXN001234569'
      },
      {
        id: 4,
        type: 'winnings',
        amount: 200.00,
        description: 'Bingo Game Winnings',
        date: '2025-01-18T16:10:00Z',
        status: 'completed',
        reference: 'TXN001234570'
      },
      {
        id: 5,
        type: 'deposit',
        amount: 1000.00,
        description: 'Bank Transfer Deposit',
        date: '2025-01-17T09:15:00Z',
        status: 'pending',
        reference: 'TXN001234571'
      },
      {
        id: 6,
        type: 'game_fee',
        amount: 50.00,
        description: 'Premium Bingo Entry',
        date: '2025-01-16T20:30:00Z',
        status: 'completed',
        reference: 'TXN001234572'
      }
    ];
    setTransactions(mockTransactions);
  }, []);

  const filteredTransactions = transactions.filter(transaction => {
    const matchesFilter = filter === 'all' || transaction.type === filter;
    const matchesSearch = transaction.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         transaction.reference.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'deposit':
        return <ArrowDown className="w-5 h-5 text-green-400" />;
      case 'withdrawal':
        return <ArrowUp className="w-5 h-5 text-red-400" />;
      case 'game_fee':
        return <DollarSign className="w-5 h-5 text-yellow-400" />;
      case 'winnings':
        return <DollarSign className="w-5 h-5 text-green-400" />;
      default:
        return <DollarSign className="w-5 h-5 text-gray-400" />;
    }
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'deposit':
      case 'winnings':
        return 'text-green-400';
      case 'withdrawal':
      case 'game_fee':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const formatAmount = (amount, type) => {
    const sign = (type === 'withdrawal' || type === 'game_fee') ? '-' : '+';
    return `${sign}ETB ${amount.toLocaleString()}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalDeposits = transactions
    .filter(t => t.type === 'deposit' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalWithdrawals = transactions
    .filter(t => t.type === 'withdrawal' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalGameFees = transactions
    .filter(t => t.type === 'game_fee' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalWinnings = transactions
    .filter(t => t.type === 'winnings' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="min-h-screen w-full bg-gray-900 text-white overflow-y-auto">
      <div className="container mx-auto px-4 py-8 w-full">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold">Transaction History</h1>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <select className="bg-gray-700 p-2 rounded-lg w-full sm:w-auto">
              <option>Last 30 days</option>
              <option>Last 7 days</option>
              <option>Today</option>
            </select>
            <button className="bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors w-full sm:w-auto">
              Export
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8 w-full">
          <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base sm:text-lg font-semibold text-white">Total Deposits</h3>
              <div className="bg-green-600 p-2 rounded-lg">
                <ArrowDown className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl font-bold text-green-400 mt-2">
              ETB {totalDeposits.toLocaleString()}
            </p>
          </div>

          <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base sm:text-lg font-semibold text-white">Total Withdrawals</h3>
              <div className="bg-red-600 p-2 rounded-lg">
                <ArrowUp className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl font-bold text-red-400 mt-2">
              ETB {totalWithdrawals.toLocaleString()}
            </p>
          </div>

          <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base sm:text-lg font-semibold text-white">Game Fees</h3>
              <div className="bg-yellow-600 p-2 rounded-lg">
                <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl font-bold text-yellow-400 mt-2">
              ETB {totalGameFees.toLocaleString()}
            </p>
          </div>

          <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base sm:text-lg font-semibold text-white">Total Winnings</h3>
              <div className="bg-green-600 p-2 rounded-lg">
                <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
            </div>
            <p className="text-xl sm:text-2xl font-bold text-green-400 mt-2">
              ETB {totalWinnings.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 p-4 sm:p-6 rounded-xl mb-6 w-full">
          <div className="flex flex-col lg:flex-row gap-4 items-stretch lg:items-center justify-between">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select 
                  className="bg-gray-700 p-2 rounded-lg w-full sm:w-auto"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">All Transactions</option>
                  <option value="deposit">Deposits</option>
                  <option value="withdrawal">Withdrawals</option>
                  <option value="game_fee">Game Fees</option>
                  <option value="winnings">Winnings</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Search className="w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search transactions..."
                className="bg-gray-700 p-2 rounded-lg w-full lg:w-64"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-gray-800 rounded-xl overflow-hidden w-full">
          <div className="overflow-x-auto max-h-96 sm:max-h-[500px] lg:max-h-[600px] overflow-y-auto">
            <table className="w-full min-w-full">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Type</th>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Description</th>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Amount</th>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Date</th>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Status</th>
                  <th className="px-3 sm:px-6 py-3 sm:py-4 text-left text-xs sm:text-sm font-semibold text-gray-300">Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredTransactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-700 transition-colors">
                    <td className="px-3 sm:px-6 py-3 sm:py-4">
                      <div className="flex items-center gap-2 sm:gap-3">
                        {getTransactionIcon(transaction.type)}
                        <span className="capitalize text-xs sm:text-sm font-medium">
                          {transaction.type.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-300">
                      <div className="truncate max-w-32 sm:max-w-none" title={transaction.description}>
                        {transaction.description}
                      </div>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4">
                      <span className={`text-xs sm:text-sm font-semibold ${getTransactionColor(transaction.type)}`}>
                        {formatAmount(transaction.amount, transaction.type)}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-300">
                      {formatDate(transaction.date)}
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        transaction.status === 'completed' 
                          ? 'bg-green-600 text-green-100' 
                          : 'bg-yellow-600 text-yellow-100'
                      }`}>
                        {transaction.status}
                      </span>
                    </td>
                    <td className="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-300 font-mono">
                      <div className="truncate max-w-24 sm:max-w-none" title={transaction.reference}>
                        {transaction.reference}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredTransactions.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-400">No transactions found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Transactions;
