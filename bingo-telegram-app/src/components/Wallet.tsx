import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WebApp } from '../utils/telegram';

interface User {
  id: number;
  username: string;
  phone: string;
  telegram_id: string;
  balance: number;
}

interface WalletProps {
  user: User | null;
  setUser: (user: User) => void;
}

const Wallet: React.FC<WalletProps> = ({ user, setUser }) => {
  const navigate = useNavigate();
  const [selectedAmount, setSelectedAmount] = useState(50);
  const [customAmount, setCustomAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [transactions, setTransactions] = useState<any[]>([]);

  const predefinedAmounts = [25, 50, 100, 200, 500, 1000];

  const handleDeposit = async () => {
    if (!user) return;

    const amount = selectedAmount === 0 ? parseFloat(customAmount) : selectedAmount;
    
    if (!amount || amount < 10) {
      WebApp.showAlert('Minimum deposit amount is 10 ETB');
      return;
    }

    setLoading(true);
    try {
      // In a real implementation, this would integrate with payment providers
      // For now, we'll simulate a successful deposit
      WebApp.showAlert(`Deposit of ${amount} ETB initiated. In a real app, this would redirect to payment.`);
      
      // Simulate successful deposit after 2 seconds
      setTimeout(() => {
        const updatedUser = { ...user, balance: user.balance + amount };
        setUser(updatedUser);
        setLoading(false);
        WebApp.showAlert(`Successfully deposited ${amount} ETB!`);
      }, 2000);

    } catch (error) {
      console.error('Error processing deposit:', error);
      WebApp.showAlert('Failed to process deposit. Please try again.');
      setLoading(false);
    }
  };

  const handleWithdraw = () => {
    if (!user || user.balance < 10) {
      WebApp.showAlert('Insufficient balance for withdrawal');
      return;
    }

    WebApp.showAlert('Withdrawal feature coming soon!');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">💳</div>
          <h1 className="text-2xl font-bold text-white mb-2">Wallet Not Found</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      {/* Header */}
      <div className="text-center mb-8">
        <button
          onClick={() => navigate('/')}
          className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg mb-4"
        >
          ← Back to Home
        </button>
        <div className="text-6xl mb-4">💳</div>
        <h1 className="text-3xl font-bold text-white mb-2">Wallet</h1>
        <p className="text-gray-300">Manage your funds</p>
      </div>

      {/* Balance Card */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 mb-6">
        <div className="text-center">
          <div className="text-white/80 text-sm mb-2">Current Balance</div>
          <div className="text-4xl font-bold text-white mb-4">{user.balance} ETB</div>
          <div className="flex justify-center space-x-4">
            <button
              onClick={handleDeposit}
              disabled={loading}
              className="bg-white/20 hover:bg-white/30 disabled:bg-white/10 text-white px-6 py-2 rounded-lg transition-colors"
            >
              {loading ? 'Processing...' : '💰 Deposit'}
            </button>
            <button
              onClick={handleWithdraw}
              className="bg-white/20 hover:bg-white/30 text-white px-6 py-2 rounded-lg transition-colors"
            >
              💸 Withdraw
            </button>
          </div>
        </div>
      </div>

      {/* Deposit Section */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-4">Add Funds</h3>
        
        {/* Predefined Amounts */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {predefinedAmounts.map((amount) => (
            <button
              key={amount}
              onClick={() => {
                setSelectedAmount(amount);
                setCustomAmount('');
              }}
              className={`p-3 rounded-lg font-semibold transition-colors ${
                selectedAmount === amount
                  ? 'bg-purple-600 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {amount} ETB
            </button>
          ))}
        </div>

        {/* Custom Amount */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Or enter custom amount
          </label>
          <input
            type="number"
            value={customAmount}
            onChange={(e) => {
              setCustomAmount(e.target.value);
              setSelectedAmount(0);
            }}
            placeholder="Enter amount (min 10 ETB)"
            min="10"
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Deposit Button */}
        <button
          onClick={handleDeposit}
          disabled={loading || (selectedAmount === 0 && (!customAmount || parseFloat(customAmount) < 10))}
          className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-600 text-white py-3 rounded-lg font-semibold transition-all transform hover:scale-105 disabled:transform-none"
        >
          {loading ? 'Processing...' : `Deposit ${selectedAmount === 0 ? customAmount : selectedAmount} ETB`}
        </button>
      </div>

      {/* Payment Methods */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-4">Payment Methods</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="text-2xl mr-3">🏦</div>
              <div>
                <div className="text-white font-semibold">Bank Transfer</div>
                <div className="text-gray-400 text-sm">Direct bank transfer</div>
              </div>
            </div>
            <div className="text-green-400">✓</div>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="text-2xl mr-3">📱</div>
              <div>
                <div className="text-white font-semibold">Mobile Money</div>
                <div className="text-gray-400 text-sm">M-Pesa, Telebirr, etc.</div>
              </div>
            </div>
            <div className="text-green-400">✓</div>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
            <div className="flex items-center">
              <div className="text-2xl mr-3">💳</div>
              <div>
                <div className="text-white font-semibold">Credit Card</div>
                <div className="text-gray-400 text-sm">Visa, Mastercard</div>
              </div>
            </div>
            <div className="text-yellow-400">Soon</div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Transactions</h3>
        {transactions.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📝</div>
            <p className="text-gray-400">No transactions yet</p>
            <p className="text-gray-500 text-sm">Your transaction history will appear here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((transaction, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                <div className="flex items-center">
                  <div className={`text-2xl mr-3 ${
                    transaction.type === 'deposit' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {transaction.type === 'deposit' ? '💰' : '💸'}
                  </div>
                  <div>
                    <div className="text-white font-semibold">
                      {transaction.type === 'deposit' ? 'Deposit' : 'Withdrawal'}
                    </div>
                    <div className="text-gray-400 text-sm">
                      {new Date(transaction.date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className={`font-semibold ${
                  transaction.type === 'deposit' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {transaction.type === 'deposit' ? '+' : '-'}{transaction.amount} ETB
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Wallet;
