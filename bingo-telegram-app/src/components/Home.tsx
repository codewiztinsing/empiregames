import React from 'react';
import { useNavigate } from 'react-router-dom';
import { WebApp } from '../utils/telegram';

interface User {
  id: number;
  username: string;
  phone: string;
  telegram_id: string;
  balance: number;
}

interface HomeProps {
  user: User | null;
}

const Home: React.FC<HomeProps> = ({ user }) => {
  const navigate = useNavigate();

  const handlePlayBingo = () => {
    navigate('/game');
  };

  const handleViewProfile = () => {
    navigate('/profile');
  };

  const handleViewWallet = () => {
    navigate('/wallet');
  };

  return (
    <div className="min-h-screen p-4">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">🎯</div>
        <h1 className="text-3xl font-bold text-white mb-2">Empire Bingo</h1>
        <p className="text-gray-300">Welcome back, {user?.username}!</p>
      </div>

      {/* Balance Card */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-300 text-sm">Your Balance</p>
            <p className="text-3xl font-bold text-white">{user?.balance || 0} ETB</p>
          </div>
          <div className="text-4xl">💰</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <button
          onClick={handlePlayBingo}
          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white p-6 rounded-2xl text-center transition-all transform hover:scale-105"
        >
          <div className="text-3xl mb-2">🎮</div>
          <div className="font-semibold">Play Bingo</div>
          <div className="text-sm opacity-90">Start a new game</div>
        </button>

        <button
          onClick={handleViewWallet}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white p-6 rounded-2xl text-center transition-all transform hover:scale-105"
        >
          <div className="text-3xl mb-2">💳</div>
          <div className="font-semibold">Wallet</div>
          <div className="text-sm opacity-90">Add funds</div>
        </button>
      </div>

      {/* Game Stats */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-4">Your Stats</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-purple-400">0</div>
            <div className="text-sm text-gray-300">Games Played</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">0</div>
            <div className="text-sm text-gray-300">Games Won</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-400">0</div>
            <div className="text-sm text-gray-300">Total Winnings</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={handleViewProfile}
          className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl transition-colors"
        >
          👤 Profile
        </button>
        <button
          onClick={() => WebApp.showAlert('Support: @empiregames_support')}
          className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl transition-colors"
        >
          🆘 Support
        </button>
      </div>
    </div>
  );
};

export default Home;
