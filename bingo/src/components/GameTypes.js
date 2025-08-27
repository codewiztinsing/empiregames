import React, { useState, useEffect } from 'react';
import { getGames } from '../services/api';
import AddGame from './AddGame';

const Games = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddGame, setShowAddGame] = useState(false);

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      const response = await getGames();
      setGames(response.data);
    } catch (error) {
      console.error('Error fetching games:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (gameId) => {
    // Edit functionality
    console.log('Edit game:', gameId);
  };

  const handleDelete = (gameId) => {
    // Delete functionality
    console.log('Delete game:', gameId);
    // Example: remove from UI (local state)
    setGames((prev) => prev.filter((g) => g.id !== gameId));
  };

  if (loading) {
    return <div className="text-white">Loading games...</div>;
  }

  return (
    <div className="min-w-3/4 p-6 m-auto max-h-screen overflow-y-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Game Management</h1>

      <div className="mb-6">
        <button
          className="bg-green-500 hover:bg-green-600 px-6 py-2 rounded text-white font-medium transition-colors"
          onClick={() => setShowAddGame(true)}
        >
          Add New Game
        </button>
      </div>

      {showAddGame ? (
        <AddGame />
      ) : (
        <div className="space-y-4">
          {games.map((game, index) => (
            <div key={game.id} className="bg-gray-800 rounded-lg p-4 text-white">
              <div className="flex justify-between items-center">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">
                    Room ID: room_{game.id || index + 10}
                  </h3>

                  <div className="grid grid-cols-2 gap-6 text-sm">
                    <div>
                      <p>Stake: {game.betAmount || '10.00'} birr</p>
                      <p>Min Players: {game.minPlayers || 2}</p>
                      <p>Draw Speed: {game.drawSpeed || 3} seconds</p>
                    </div>
                    <div>
                      <p>Commission: {game.commission || '70.00'}%</p>
                      <p>Max Players: {game.maxPlayers || 100}</p>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(game.id)}
                    className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded text-white transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(game.id)}
                    className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-white transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}

          {games.length === 0 && (
            <div className="text-gray-400 text-center py-8">
              No games found
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Games;
