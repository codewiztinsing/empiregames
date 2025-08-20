import React, { useState, useEffect } from 'react';
import { Users, DollarSign, Gift, TrendingUp, Share2, Copy, Check, UserPlus, Eye, MoreVertical } from 'lucide-react';

function Referrals() {
  const [referrals, setReferrals] = useState([]);
  const [stats, setStats] = useState({
    totalReferrals: 0,
    activeReferrals: 0,
    totalCommission: 0,
    conversionRate: 0
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [copiedCode, setCopiedCode] = useState(false);
  const [referralCode] = useState('BINGO2024-USER123');

  useEffect(() => {
    fetchReferrals();
    fetchStats();
  }, []);

  const fetchReferrals = () => {
    // Mock data - replace with actual API call
    const mockReferrals = [
      {
        id: 1,
        referredUser: 'John Doe',
        email: 'john@example.com',
        dateReferred: '2024-01-15',
        status: 'Active',
        gamesPlayed: 12,
        commission: 150.00,
        totalSpent: 500.00
      },
      {
        id: 2,
        referredUser: 'Jane Smith',
        email: 'jane@example.com',
        dateReferred: '2024-01-10',
        status: 'Active',
        gamesPlayed: 8,
        commission: 80.00,
        totalSpent: 320.00
      },
      {
        id: 3,
        referredUser: 'Mike Johnson',
        email: 'mike@example.com',
        dateReferred: '2024-01-05',
        status: 'Inactive',
        gamesPlayed: 3,
        commission: 25.00,
        totalSpent: 100.00
      },
      {
        id: 4,
        referredUser: 'Sarah Wilson',
        email: 'sarah@example.com',
        dateReferred: '2024-01-20',
        status: 'Active',
        gamesPlayed: 15,
        commission: 200.00,
        totalSpent: 750.00
      }
    ];
    setReferrals(mockReferrals);
  };

  const fetchStats = () => {
    // Mock stats - replace with actual API call
    setStats({
      totalReferrals: 4,
      activeReferrals: 3,
      totalCommission: 455.00,
      conversionRate: 75
    });
  };

  const filteredReferrals = referrals.filter(referral => {
    const matchesSearch = referral.referredUser.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         referral.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || referral.status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-600 text-green-100';
      case 'inactive':
        return 'bg-gray-600 text-gray-100';
      default:
        return 'bg-gray-600 text-gray-100';
    }
  };

  const formatAmount = (amount) => {
    return `ETB ${amount.toLocaleString()}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const copyReferralCode = () => {
    navigator.clipboard.writeText(referralCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const shareReferralLink = () => {
    const referralLink = `https://bingo.app/signup?ref=${referralCode}`;
    if (navigator.share) {
      navigator.share({
        title: 'Join Bingo Game',
        text: 'Join me on this amazing bingo platform!',
        url: referralLink
      });
    } else {
      navigator.clipboard.writeText(referralLink);
      alert('Referral link copied to clipboard!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Referral Program</h1>
          <p className="text-gray-400">Invite friends and earn commissions from their gameplay</p>
        </div>

        {/* Referral Code Section */}
        <div className="bg-gray-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Your Referral Code</h2>
          <div className="flex items-center gap-4 mb-4">
            <div className="bg-gray-700 px-4 py-3 rounded-lg flex-1">
              <span className="font-mono text-lg text-green-400">{referralCode}</span>
            </div>
            <button
              onClick={copyReferralCode}
              className="bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
            >
              {copiedCode ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copiedCode ? 'Copied!' : 'Copy'}
            </button>
            <button
              onClick={shareReferralLink}
              className="bg-green-600 hover:bg-green-700 px-4 py-3 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Share2 className="w-4 h-4" />
              Share
            </button>
          </div>
          <p className="text-gray-400 text-sm">
            Share this code with friends to earn 10% commission on their gameplay
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Total Referrals</h3>
              <div className="bg-blue-600 p-2 rounded-lg">
                <Users className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{stats.totalReferrals}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Active Referrals</h3>
              <div className="bg-green-600 p-2 rounded-lg">
                <UserPlus className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{stats.activeReferrals}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Total Commission</h3>
              <div className="bg-yellow-600 p-2 rounded-lg">
                <DollarSign className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{formatAmount(stats.totalCommission)}</p>
          </div>

          <div className="bg-gray-800 p-6 rounded-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Conversion Rate</h3>
              <div className="bg-purple-600 p-2 rounded-lg">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{stats.conversionRate}%</p>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-gray-800 p-6 rounded-xl mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex items-center gap-4 w-full sm:w-auto">
              <input
                type="text"
                placeholder="Search referrals..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500 flex-1 sm:w-64"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        {/* Referrals Table */}
        <div className="bg-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Referred User
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Date Referred
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Games Played
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Total Spent
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Commission
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredReferrals.map((referral) => (
                  <tr key={referral.id} className="hover:bg-gray-700 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-semibold text-white">{referral.referredUser}</div>
                        <div className="text-sm text-gray-400">{referral.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {formatDate(referral.dateReferred)}
                    </td>
                    <td className="px-6 py-4 text-sm text-white font-semibold">
                      {referral.gamesPlayed}
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-semibold text-white">
                        {formatAmount(referral.totalSpent)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-semibold text-green-400">
                        {formatAmount(referral.commission)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(referral.status)}`}>
                        {referral.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors">
                          <Eye className="w-4 h-4" />
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
          
          {filteredReferrals.length === 0 && (
            <div className="text-center py-12">
              <Gift className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-400">No referrals found.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Referrals;
