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

interface ProfileProps {
  user: User | null;
  setUser: (user: User) => void;
}

const Profile: React.FC<ProfileProps> = ({ user, setUser }) => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState(user?.phone || '');
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleUpdatePhone = async () => {
    if (!user || !phone) return;

    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: phone,
        }),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        setIsEditing(false);
        WebApp.showAlert('Phone number updated successfully!');
      } else {
        WebApp.showAlert('Failed to update phone number');
      }
    } catch (error) {
      console.error('Error updating phone:', error);
      WebApp.showAlert('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeposit = () => {
    navigate('/wallet');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">👤</div>
          <h1 className="text-2xl font-bold text-white mb-2">Profile Not Found</h1>
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
        <div className="text-6xl mb-4">👤</div>
        <h1 className="text-3xl font-bold text-white mb-2">Profile</h1>
        <p className="text-gray-300">Manage your account information</p>
      </div>

      {/* Profile Card */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-bold text-white">
              {user.username.charAt(0).toUpperCase()}
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white">{user.username}</h2>
          <p className="text-gray-300">Telegram ID: {user.telegram_id}</p>
        </div>

        {/* User Info */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Username
            </label>
            <input
              type="text"
              value={user.username}
              disabled
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white cursor-not-allowed"
            />
            <p className="text-xs text-gray-400 mt-1">Username cannot be changed</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Phone Number
            </label>
            {isEditing ? (
              <div className="flex space-x-2">
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Enter your phone number"
                  className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <button
                  onClick={handleUpdatePhone}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-colors"
                >
                  {loading ? '...' : '✓'}
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setPhone(user.phone);
                  }}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-3 rounded-lg transition-colors"
                >
                  ✕
                </button>
              </div>
            ) : (
              <div className="flex space-x-2">
                <input
                  type="tel"
                  value={user.phone || 'Not set'}
                  disabled
                  className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white cursor-not-allowed"
                />
                <button
                  onClick={() => setIsEditing(true)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg transition-colors"
                >
                  ✏️
                </button>
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Balance
            </label>
            <div className="flex items-center justify-between px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg">
              <span className="text-white font-semibold">{user.balance} ETB</span>
              <button
                onClick={handleDeposit}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                Add Funds
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-4">Game Statistics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">0</div>
            <div className="text-sm text-gray-300">Games Played</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">0</div>
            <div className="text-sm text-gray-300">Games Won</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">0</div>
            <div className="text-sm text-gray-300">Total Winnings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">0%</div>
            <div className="text-sm text-gray-300">Win Rate</div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-4">
        <button
          onClick={() => WebApp.showAlert('Support: @empiregames_support')}
          className="w-full bg-white/10 hover:bg-white/20 text-white p-4 rounded-xl transition-colors"
        >
          🆘 Contact Support
        </button>
        
        <button
          onClick={() => WebApp.showAlert('Terms of Service and Privacy Policy will be available soon.')}
          className="w-full bg-white/10 hover:bg-white/20 text-white p-4 rounded-xl transition-colors"
        >
          📋 Terms & Privacy
        </button>
      </div>
    </div>
  );
};

export default Profile;
