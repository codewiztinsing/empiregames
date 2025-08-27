import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Filter,
  MoreVertical,
  UserPlus,
  Mail,
  Phone,
  Calendar,
  DollarSign,
  Edit,
  Trash2,
  UserCheck,
  UserX
} from 'lucide-react';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { getAllUsers, deleteUser } from '../services/api';
import EditPlayer from './EditPlayer';

function Players() {
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [playersPerPage] = useState(10);
  const [editPlayer, setEditPlayer] = useState(false);
  const [telegramId, setTelegramId] = useState('');
  const [username, setUsername] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [balance, setBalance] = useState('');
  const [status, setStatus] = useState('');

  useEffect(() => {
    const fetchAllUsers = async () => {
      try {
        const allusers = await getAllUsers();
        setPlayers(allusers.data);
        setFilteredPlayers(allusers.data);
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    };
    fetchAllUsers();
  }, []);

  // Filter logic
  useEffect(() => {
    let filtered = players;

    if (searchTerm) {
      const lower = searchTerm.toLowerCase();
      filtered = filtered.filter(player =>
        player.username?.toLowerCase().includes(lower) ||
        player.phoneNumber?.toLowerCase().includes(lower) ||
        String(player.telegramId).includes(lower)
      );
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(player =>
        player.status?.toLowerCase() === filterStatus.toLowerCase()
      );
    }

    setFilteredPlayers(filtered);
    setCurrentPage(1); // Reset to first page on new filter/search
  }, [players, searchTerm, filterStatus]);

  // Helpers
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-600 text-green-100';
      case 'inactive':
        return 'bg-gray-600 text-gray-100';
      case 'suspended':
        return 'bg-red-600 text-red-100';
      default:
        return 'bg-gray-600 text-gray-100';
    }
  };

  const handleEdit = (telegramId, username, phoneNumber, balance, status) => {
    setEditPlayer(true);
    setTelegramId(telegramId);
    setUsername(username);
    setPhoneNumber(phoneNumber);
    setBalance(balance);
    setStatus(status);
  };

  const formatDate = (dateString) => {
    return dateString
      ? new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      : 'N/A';
  };

  const formatAmount = (amount) => {
    return amount != null ? `${Number(amount).toLocaleString()}` : '0';
  };

  const calculateWinRate = (won, played) => {
    return played > 0 ? ((won / played) * 100).toFixed(1) : '0.0';
  };

  const handleDelete = async (player) => {
    if (!window.confirm(`Are you sure you want to delete ${player.username}?`)) return;
    try {
      const response = await deleteUser(player.telegramId);
      if (response.status === 204) {
        setPlayers(players.filter(p => p.telegramId !== player.telegramId));
        setFilteredPlayers(filteredPlayers.filter(p => p.telegramId !== player.telegramId));
        toast.success("Player deleted successfully");
      } else {
        toast.error("Error deleting player");
      }
    } catch (error) {
      toast.error("Error deleting player");
    }
  };

  return (
    <>

    <div className='h-screen overflow-y-auto'>
    <Toaster position="top-right" reverseOrder={false} />
      
      <div className="min-h-screen bg-gray-900 p-6 w-full">
        <div className="w-full">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Players Management</h1>
              <p className="text-gray-400">Manage and monitor player activities</p>
            </div>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
            >
              <UserPlus className="w-5 h-5" />
              Add Player
            </button>
          </div>

          {/* Statistics Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
            <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
              <div className="flex items-center justify-between">
                <h3 className="text-base sm:text-lg font-semibold text-white">Total Players</h3>
                <div className="bg-blue-600 p-2 rounded-lg">
                  <Users className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-blue-400 mt-2">
                {players.length.toLocaleString()}
              </p>
            </div>

            <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
              <div className="flex items-center justify-between">
                <h3 className="text-base sm:text-lg font-semibold text-white">Active Players</h3>
                <div className="bg-green-600 p-2 rounded-lg">
                  <UserCheck className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-green-400 mt-2">
                {players.filter(p => p.status?.toLowerCase() === 'active').length.toLocaleString()}
              </p>
            </div>

            <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
              <div className="flex items-center justify-between">
                <h3 className="text-base sm:text-lg font-semibold text-white">Suspended Players</h3>
                <div className="bg-red-600 p-2 rounded-lg">
                  <UserX className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-red-400 mt-2">
                {players.filter(p => p.status?.toLowerCase() === 'suspended').length.toLocaleString()}
              </p>
            </div>

            <div className="bg-gray-800 p-4 sm:p-6 rounded-xl">
              <div className="flex items-center justify-between">
                <h3 className="text-base sm:text-lg font-semibold text-white">Total Balance</h3>
                <div className="bg-yellow-600 p-2 rounded-lg">
                  <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-yellow-400 mt-2">
                ETB {players.reduce((sum, p) => sum + (p.balance || 0), 0).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-gray-800 p-6 rounded-xl mb-6 overflow-x-auto ">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search players by name, phone, or ID..."
                  className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
            </div>
          </div>

          {/* Players Table (page scroll instead of inner scroll) */}
          <div className="bg-gray-800 rounded-xl overflow-x-auto w-full">
            <table className="w-full min-w-[1000px]">
              <thead className="bg-gray-700 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Player</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Contact</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Join Date</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Games</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Win Rate</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Balance</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredPlayers
                  .slice((currentPage - 1) * playersPerPage, currentPage * playersPerPage)
                  .map((player) => (
                    <tr key={player.telegramId} className="hover:bg-gray-700 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold">
                              {player.username ? player.username.charAt(0).toUpperCase() : "?"}
                            </span>
                          </div>
                          <div>
                            <div className="font-semibold text-white">{player.username || "Unknown"}</div>
                            <div className="text-sm text-gray-400">ID: {player.telegramId}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="text-white flex items-center gap-2">
                          <Mail className="w-4 h-4 text-gray-400" />
                          {player.username || "N/A"}
                        </div>
                        <div className="text-gray-400 flex items-center gap-2 mt-1">
                          <Phone className="w-4 h-4" />
                          {player.phoneNumber || "N/A"}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          {formatDate(player.joinedAt)}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="text-white font-semibold">{player.totalGames || 0}</div>
                        <div className="text-gray-400">{player.gamesWon || 0} wins</div>
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-white">
                        {calculateWinRate(player.gamesWon || 0, player.totalGames || 0)}%
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-green-400">
                        {formatAmount(player.balance)}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(player.status)}`}>
                          {player.status || "Unknown"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                            onClick={() => handleEdit(player.telegramId, player.username, player.phoneNumber, player.balance, player.status)}
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-lg transition-colors"
                            onClick={() => handleDelete(player)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                            <MoreVertical className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>

            {filteredPlayers.length === 0 && (
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">No players found.</p>
              </div>
            )}
          </div>

          {/* Pagination */}
          <div className="flex justify-center items-center mt-6 gap-4">
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg"
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <p className="text-gray-400">
              Page {filteredPlayers.length > 0 ? currentPage : 0} of{" "}
              {Math.max(1, Math.ceil(filteredPlayers.length / playersPerPage))}
            </p>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg"
              disabled={currentPage === Math.ceil(filteredPlayers.length / playersPerPage) || filteredPlayers.length === 0}
            >
              Next
            </button>
          </div>
        </div>

        {/* Edit Player Modal */}
        {editPlayer && (
          <EditPlayer
            playerId={telegramId}
            username={username}
            phoneNumber={phoneNumber}
            balance={balance}
            status={status}
            onClose={() => setEditPlayer(false)}
          />
        )}
      </div>
    </div>
   
    </>
  );
}

export default Players;
