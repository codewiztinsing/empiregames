import React, { useState, useMemo } from 'react';
import { 
  CreditCard, 
  DollarSign, 
  Calendar, 
  Search, 
  Filter, 
  Download,
  Eye,
  MoreVertical,
  TrendingUp,
  TrendingDown,
  Clock
} from 'lucide-react';

function Payments() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [methodFilter, setMethodFilter] = useState('all');

  // Mock payments data
  const payments = [
    {
      id: 'PAY001',
      playerId: 'USR001',
      playerName: 'John Doe',
      amount: 50.00,
      method: 'credit_card',
      status: 'completed',
      date: '2024-01-15T10:30:00Z',
      reference: 'TXN_123456789',
      description: 'Game entry fee',
      fee: 2.50
    },
    {
      id: 'PAY002',
      playerId: 'USR002',
      playerName: 'Jane Smith',
      amount: 25.00,
      method: 'paypal',
      status: 'pending',
      date: '2024-01-15T09:15:00Z',
      reference: 'TXN_987654321',
      description: 'Prize withdrawal',
      fee: 1.25
    },
    {
      id: 'PAY003',
      playerId: 'USR003',
      playerName: 'Mike Johnson',
      amount: 100.00,
      method: 'bank_transfer',
      status: 'failed',
      date: '2024-01-14T16:45:00Z',
      reference: 'TXN_456789123',
      description: 'Account deposit',
      fee: 5.00
    },
    {
      id: 'PAY004',
      playerId: 'USR004',
      playerName: 'Sarah Wilson',
      amount: 75.00,
      method: 'credit_card',
      status: 'completed',
      date: '2024-01-14T14:20:00Z',
      reference: 'TXN_789123456',
      description: 'Game entry fee',
      fee: 3.75
    },
    {
      id: 'PAY005',
      playerId: 'USR005',
      playerName: 'David Brown',
      amount: 200.00,
      method: 'crypto',
      status: 'completed',
      date: '2024-01-13T11:10:00Z',
      reference: 'TXN_321654987',
      description: 'Prize withdrawal',
      fee: 10.00
    }
  ];

  const filteredPayments = useMemo(() => {
    return payments.filter(payment => {
      const matchesSearch = payment.playerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           payment.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           payment.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || payment.status === statusFilter;
      const matchesMethod = methodFilter === 'all' || payment.method === methodFilter;
      
      return matchesSearch && matchesStatus && matchesMethod;
    });
  }, [searchTerm, statusFilter, methodFilter]);

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-600 text-green-100';
      case 'pending':
        return 'bg-yellow-600 text-yellow-100';
      case 'failed':
        return 'bg-red-600 text-red-100';
      default:
        return 'bg-gray-600 text-gray-100';
    }
  };

  const getPaymentMethodIcon = (method) => {
    switch (method) {
      case 'credit_card':
        return <CreditCard className="w-4 h-4 text-blue-400" />;
      case 'paypal':
        return <DollarSign className="w-4 h-4 text-blue-400" />;
      case 'bank_transfer':
        return <TrendingUp className="w-4 h-4 text-green-400" />;
      case 'crypto':
        return <TrendingDown className="w-4 h-4 text-orange-400" />;
      default:
        return <DollarSign className="w-4 h-4 text-gray-400" />;
    }
  };

  const getPaymentMethodLabel = (method) => {
    switch (method) {
      case 'credit_card':
        return 'Credit Card';
      case 'paypal':
        return 'PayPal';
      case 'bank_transfer':
        return 'Bank Transfer';
      case 'crypto':
        return 'Cryptocurrency';
      default:
        return method;
    }
  };

  const totalAmount = filteredPayments.reduce((sum, payment) => sum + payment.amount, 0);
  const totalFees = filteredPayments.reduce((sum, payment) => sum + payment.fee, 0);
  const completedPayments = filteredPayments.filter(p => p.status === 'completed').length;
  const pendingPayments = filteredPayments.filter(p => p.status === 'pending').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Payments</h1>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Volume</p>
              <p className="text-2xl font-bold text-white">{formatAmount(totalAmount)}</p>
            </div>
            <DollarSign className="w-8 h-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Fees</p>
              <p className="text-2xl font-bold text-white">{formatAmount(totalFees)}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-white">{completedPayments}</p>
            </div>
            <CreditCard className="w-8 h-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Pending</p>
              <p className="text-2xl font-bold text-white">{pendingPayments}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-400" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 p-6 rounded-lg">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search by player, reference, or payment ID..."
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex gap-4">
            <select
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
            
            <select
              className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={methodFilter}
              onChange={(e) => setMethodFilter(e.target.value)}
            >
              <option value="all">All Methods</option>
              <option value="credit_card">Credit Card</option>
              <option value="paypal">PayPal</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="crypto">Cryptocurrency</option>
            </select>
          </div>
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Payment ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Player
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Fee
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Reference
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredPayments.map((payment) => (
                <tr key={payment.id} className="hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-white">
                    {payment.id}
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-white">{payment.playerName}</div>
                      <div className="text-sm text-gray-400">{payment.playerId}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getPaymentMethodIcon(payment.method)}
                      <span className="text-sm text-white">{getPaymentMethodLabel(payment.method)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm font-semibold text-green-400">
                      {formatAmount(payment.amount)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-gray-300">
                      {formatAmount(payment.fee)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(payment.status)}`}>
                      {payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {formatDate(payment.date)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300 font-mono">
                    {payment.reference}
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
        
        {filteredPayments.length === 0 && (
          <div className="text-center py-12">
            <CreditCard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-400">No payments found.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Payments;
