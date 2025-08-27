import React, { useState } from 'react';
import { createGame } from '../services/api';

const AddGame = () => {
  const [formData, setFormData] = useState({
    betAmount: '',
    minPlayers: '',
    maxPlayers: '',
    drawSpeed: '',
    commission: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const gameData = {
        betAmount: parseFloat(formData.betAmount),
        minPlayers: parseInt(formData.minPlayers),
        maxPlayers: parseInt(formData.maxPlayers),
        drawSpeed: parseInt(formData.drawSpeed),
        commission: parseFloat(formData.commission)
      };

      await createGame(gameData);
      setMessage('Game created successfully!');
      setFormData({
        betAmount: '',
        minPlayers: '',
        maxPlayers: '',
        drawSpeed: '',
        commission: ''
      });
    } catch (error) {
      setMessage('Error creating game: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-w-3/4 p-6 m-auto max-h-screen overflow-y-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Add New Game</h1>
      
      <div className="bg-gray-800 rounded-lg p-6 max-w-md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Stake Amount (birr)
            </label>
            <input
              type="number"
              step="0.01"
              name="betAmount"
              value={formData.betAmount}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Minimum Players
            </label>
            <input
              type="number"
              name="minPlayers"
              value={formData.minPlayers}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Maximum Players
            </label>
            <input
              type="number"
              name="maxPlayers"
              value={formData.maxPlayers}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Draw Speed (seconds)
            </label>
            <input
              type="number"
              name="drawSpeed"
              value={formData.drawSpeed}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Commission (%)
            </label>
            <input
              type="number"
              step="0.01"
              name="commission"
              value={formData.commission}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-medium py-2 px-4 rounded transition-colors"
          >
            {loading ? 'Creating...' : 'Create Game'}
          </button>

          {message && (
            <div className={`text-sm p-3 rounded ${
              message.includes('Error') 
                ? 'bg-red-500 text-white' 
                : 'bg-green-500 text-white'
            }`}>
              {message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default AddGame;
