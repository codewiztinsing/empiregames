import React, { useState, useEffect } from 'react';
import { getGames } from '../services/api';
import { ChevronLeft, ChevronRight, Calendar, Users, Clock, DollarSign, Play } from 'lucide-react';

function Games() {
  const [currentPage, setCurrentPage] = useState(1);
  const gamesPerPage = 10;
  const [allGames, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddGame, setShowAddGame] = useState(false);


  useEffect(() => {
    getGames()
      .then(response => {
        const games = response.data.map(game => ({
            name: "Classic Bingo Night",
            gameType: "Traditional 75-Ball",
            status: game.status,
            players: game.players,
            prize:  `ETB 0`,
            startTime: game.createdAt,
            endTime: game.createdAt,
            pattern: "Full House"
        }));
        setGames(games);
        console.log(games);
      })
      .catch(error => {
        setError(error);
        console.log(error);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleAddGame = () => {
    setShowAddGame(true);
  }



  // Calculate pagination
  const totalPages = Math.ceil(allGames.length / gamesPerPage);
  const startIndex = (currentPage - 1) * gamesPerPage;
  const endIndex = startIndex + gamesPerPage;
  const currentGames = allGames.slice(startIndex, endIndex);
  console.log("allGames",allGames);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-600';
      case 'Completed':
        return 'bg-gray-600';
      case 'Scheduled':
        return 'bg-blue-600';
      default:
        return 'bg-gray-600';
    }
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      {/* Filters Section */}
      <div className="mb-6 bg-gray-800 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500">
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Completed">Completed</option>
              <option value="Scheduled">Scheduled</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Game Type</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500">
              <option value="">All Types</option>
              <option value="Traditional 75-Ball">Traditional 75-Ball</option>
              <option value="Speed Bingo">Speed Bingo</option>
              <option value="Progressive">Progressive</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Date Range</label>
            <select className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="last7days">Last 7 Days</option>
              <option value="last30days">Last 30 Days</option>
              <option value="last90days">Last 90 Days</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
            <input
              type="text"
              placeholder="Search games..."
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="flex justify-between items-center mt-4">
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white transition-colors">
            Apply Filters
          </button>
          <button className="text-gray-400 hover:text-white transition-colors">
            Clear All
          </button>
        </div>
      </div>

      {/* Game Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Total Games</h3>
              <p className="text-3xl font-bold text-blue-400">{allGames.length}</p>
            </div>
            <div className="bg-blue-500 p-3 rounded-full">
              <Play className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Active Games</h3>
              <p className="text-3xl font-bold text-green-400">
                {allGames.filter(game => game.status === 'Active').length}
              </p>
            </div>
            <div className="bg-green-500 p-3 rounded-full">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Total Players</h3>
              <p className="text-3xl font-bold text-purple-400">
                {allGames.reduce((total, game) => total + (game.players || 0), 0)}
              </p>
            </div>
            <div className="bg-purple-500 p-3 rounded-full">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">Total Prize Pool</h3>
              <p className="text-3xl font-bold text-yellow-400">
                {allGames.reduce((total, game) => total + parseFloat(game.prize?.replace(/[^0-9.-]+/g, '') || 0), 0).toFixed(2)} ETB
              </p>
            </div>
            <div className="bg-yellow-500 p-3 rounded-full">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>



      <div className="max-w-7xl mx-auto">
       
        <div className="bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Game</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Players</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Total Win</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Winner</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Time stamp</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Pattern</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {currentGames.map((game) => (
                  <tr key={game.id} className="hover:bg-gray-750 transition-colors duration-150">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-white font-medium">{game.name}</div>
                      <div className="text-gray-400 text-sm">ID: {game.id}</div>
                    </td>
                   
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${getStatusColor(game.status)}`}>
                        {game.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-gray-300">
                        <Users className="w-4 h-4 mr-2" />
                        {game.players || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-green-400">
                        {game.prize}
                      </div>
                    </td>

                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-gray-300">{game.winner || "N/A"}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-gray-300">
                        <div className="flex items-center text-sm">
                          <Calendar className="w-4 h-4 mr-2" />
                          {new Date(game.startTime).toLocaleDateString()}
                        </div>
                        <div className="flex items-center text-sm text-gray-400">
                          <Clock className="w-4 h-4 mr-2" />
                          {new Date(game.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(game.endTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-gray-300">{game.pattern}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button className="text-indigo-400 hover:text-indigo-300 transition-colors duration-150">
                          View
                        </button>
                        <button className="text-yellow-400 hover:text-yellow-300 transition-colors duration-150">
                          Edit
                        </button>
                        <button className="text-red-400 hover:text-red-300 transition-colors duration-150">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-6">
          <div className="text-gray-400 text-sm">
            Showing {startIndex + 1} to {Math.min(endIndex, allGames.length)} of {allGames.length} games
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className={`flex items-center px-3 py-2 rounded-lg transition-colors duration-200 ${
                currentPage === 1
                  ? 'text-gray-500 cursor-not-allowed'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous
            </button>
            
            <div className="flex space-x-1">
              {[...Array(totalPages)].map((_, index) => {
                const page = index + 1;
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-2 rounded-lg transition-colors duration-200 ${
                      currentPage === page
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`flex items-center px-3 py-2 rounded-lg transition-colors duration-200 ${
                currentPage === totalPages
                  ? 'text-gray-500 cursor-not-allowed'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </div>

       
      </div>
    </div>
  );
}

export default Games;
