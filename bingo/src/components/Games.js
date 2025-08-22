import React, { useState, useEffect } from 'react';
import { getGames } from '../services/api';
import { ChevronLeft, ChevronRight, Calendar, Users, Clock, DollarSign } from 'lucide-react';

function Games() {
  const [currentPage, setCurrentPage] = useState(1);
  const gamesPerPage = 10;
  const [allGames, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-white">Games Management</h1>
         
        </div>

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

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Total Games</h3>
              <div className="bg-blue-600 p-2 rounded-lg">
                <Calendar className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{allGames.length}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Active Games</h3>
              <div className="bg-green-600 p-2 rounded-lg">
                <Clock className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">
              {allGames.filter(game => game.status === 'Active').length}
            </p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Total Players</h3>
              <div className="bg-purple-600 p-2 rounded-lg">
                <Users className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">
              {allGames.reduce((total, game) => total + game.players, 0)}
            </p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Total Prizes</h3>
              <div className="bg-yellow-600 p-2 rounded-lg">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">
              ETB {allGames.reduce((total, game) => total + parseFloat(game.prize.replace('ETB ', '').replace(',', '')), 0).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Games;
