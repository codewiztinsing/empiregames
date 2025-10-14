import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WebApp } from './utils/telegram';
import './App.css';

// Components
import Home from './components/Home';
import BingoGame from './components/BingoGame';
import Profile from './components/Profile';
import Wallet from './components/Wallet';
import Loading from './components/Loading';

// Types
interface User {
  id: number;
  username: string;
  phone: string;
  telegram_id: string;
  balance: number;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Initialize Telegram WebApp
    WebApp.ready();
    WebApp.expand();

    // Get user data from Telegram
    const initUser = async () => {
      try {
        const tgUser = WebApp.initDataUnsafe?.user;
        
        if (!tgUser) {
          setError('Unable to get user data from Telegram');
          setLoading(false);
          return;
        }

        // Check if user exists in backend or create new user
        const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/users/telegram/${tgUser.id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else if (response.status === 404) {
          // User doesn't exist, create new user
          const newUserResponse = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/users/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: tgUser.username || `user_${tgUser.id}`,
              phone: '', // Will be collected later
              telegram_id: tgUser.id.toString(),
              password: 'telegram_user', // Default password for telegram users
            }),
          });

          if (newUserResponse.ok) {
            const newUserData = await newUserResponse.json();
            setUser(newUserData);
          } else {
            setError('Failed to create user account');
          }
        } else {
          setError('Failed to authenticate user');
        }
      } catch (err) {
        console.error('Error initializing user:', err);
        setError('Network error. Please check your connection.');
      } finally {
        setLoading(false);
      }
    };

    initUser();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 text-center max-w-md w-full">
          <div className="text-red-400 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-white mb-4">Error</h1>
          <p className="text-gray-300 mb-6">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <Routes>
          <Route path="/" element={<Home user={user} />} />
          <Route path="/game" element={<BingoGame user={user} />} />
          <Route path="/profile" element={<Profile user={user} setUser={setUser} />} />
          <Route path="/wallet" element={<Wallet user={user} setUser={setUser} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;