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
  Trophy,
  DollarSign,
  Edit,
  Trash2
} from 'lucide-react';

function Players() {
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showAddPlayer, setShowAddPlayer] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  // Mock data
  useEffect(() => {
    const mockPlayers = [
      {
        id: 1,
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+251 912 345 678',
        joinDate: '2024-01-15',
        status: 'active',
        gamesPlayed: 24,
        gamesWon: 5,
        totalWinnings: 15000,
        avatar: null
      },
      {
        id: 2,
        name: 'Sarah Johnson',
        email: 'sarah.j@example.com',
        phone: '+251 911 234 567',
        joinDate: '2024-02-03',
        status: 'active',
        gamesPlayed: 18,
        gamesWon: 3,
        totalWinnings: 8500,
        avatar: null
      },
      {
        id: 3,
        name: 'Michael Brown',
        email: 'mike.brown@example.com',
        phone: '+251 913 456 789',
        joinDate: '2024-01-28',
        status: 'inactive',
        gamesPlayed: 12,
        gamesWon: 1,
        totalWinnings: 2000,
        avatar: null
      },
      {
        id: 4,
        name: 'Emily Davis',
        email: 'emily.davis@example.com',
        phone: '+251 914 567 890',
        joinDate: '2024-03-10',
        status: 'active',
        gamesPlayed: 30,
        gamesWon: 8,
        totalWinnings: 22000,
        avatar: null
      },
      {
        id: 5,
        name: 'David Wilson',
        email: 'david.w@example.com',
        phone: '+251 915 678 901',
        joinDate: '2024-02-20',
        status: 'suspended',
        gamesPlayed: 15,
        gamesWon: 2,
        totalWinnings: 4500,
        avatar: null
      }
    ];
    setPlayers(mockPlayers);
    setFilteredPlayers(mockPlayers);
  }, []);

  // Filter players based on search and status
  useEffect(() => {
    let filtered = players;

    if (searchTerm) {
      filtered = filtered.filter(player =>
        player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.phone.includes(searchTerm)
      );
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(player => player.status === filterStatus);
    }

    setFilteredPlayers(filtered);
  }, [players, searchTerm, filterStatus]);

  const getStatusColor = (status) => {
    switch (status) {
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatAmount = (amount) => {
    return `ETB ${amount.toLocaleString()}`;
  };

  const calculateWinRate = (won, played) => {
    return played > 0 ? ((won / played) * 100).toFixed(1) : '0.0';
  };

  const PlayerStats = () => {
    const totalPlayers = players.length;
    const activePlayers = players.filter(p => p.status === 'active').length;
    const totalGamesPlayed = players.reduce((sum, p) => sum + p.gamesPlayed, 0);
    const totalWinnings = players.reduce((sum, p) => sum + p.totalWinnings, 0);

    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Total Players</h3>
            <div className="bg-blue-600 p-2 rounded-lg">
              <Users className="w-5 h-5 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{totalPlayers}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Active Players</h3>
            <div className="bg-green-600 p-2 rounded-lg">
              <UserPlus className="w-5 h-5 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{activePlayers}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Games Played</h3>
            <div className="bg-purple-600 p-2 rounded-lg">
              <Trophy className="w-5 h-5 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{totalGamesPlayed}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Total Winnings</h3>
            <div className="bg-yellow-600 p-2 rounded-lg">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{formatAmount(totalWinnings)}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Players Management</h1>
            <p className="text-gray-400">Manage and monitor player activities</p>
          </div>
          <button
            onClick={() => setShowAddPlayer(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
          >
            <UserPlus className="w-5 h-5" />
            Add Player
          </button>
        </div>

        {/* Stats */}
        <PlayerStats />

        {/* Filters */}
        <div className="bg-gray-800 p-6 rounded-xl mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search players by name, email, or phone..."
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

        {/* Players Table */}
        <div className="bg-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Player</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Contact</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Join Date</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Games</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Win Rate</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Winnings</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredPlayers.map((player) => (
                  <tr key={player.id} className="hover:bg-gray-700 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-white font-semibold">
                            {player.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <div className="font-semibold text-white">{player.name}</div>
                          <div className="text-sm text-gray-400">ID: {player.id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="text-white flex items-center gap-2">
                          <Mail className="w-4 h-4 text-gray-400" />
                          {player.email}
                        </div>
                        <div className="text-gray-400 flex items-center gap-2 mt-1">
                          <Phone className="w-4 h-4" />
                          {player.phone}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        {formatDate(player.joinDate)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        <div className="text-white font-semibold">{player.gamesPlayed}</div>
                        <div className="text-gray-400">{player.gamesWon} wins</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-semibold text-white">
                        {calculateWinRate(player.gamesWon, player.gamesPlayed)}%
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-semibold text-green-400">
                        {formatAmount(player.totalWinnings)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(player.status)}`}>
                        {player.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                          <Edit className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-lg transition-colors">
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
          </div>
          
          {filteredPlayers.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">No players found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Players;
