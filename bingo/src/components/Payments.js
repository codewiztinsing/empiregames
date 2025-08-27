import React, { useState, useEffect } from 'react';

const Payments = () => {
  const [activeTab, setActiveTab] = useState('withdrawalRequests');
  const [filterStatus, setFilterStatus] = useState('Pending');
  const [withdrawalRequests, setWithdrawalRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWithdrawalRequests();
  }, []);

  const fetchWithdrawalRequests = async () => {
    try {
      // Replace with actual API call:
      // const response = await getWithdrawalRequests();
      // setWithdrawalRequests(response.data);

      setWithdrawalRequests([]); // Empty placeholder for now
    } catch (error) {
      console.error('Error fetching withdrawal requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'withdrawalRequests', label: 'Withdrawal Requests' },
    { id: 'paymentSettings', label: 'Payment Settings' },
    { id: 'manualDeposit', label: 'Manual Deposit' },
    { id: 'manualWithdraw', label: 'Manual Withdraw' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'withdrawalRequests':
        return (
          <div className="space-y-4 w-full">
            <div className="flex justify-between items-center w-full">
              <h2 className="text-xl font-semibold text-white">Withdrawal Requests</h2>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Filter by status:</span>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600"
                >
                  <option value="Pending">Pending</option>
                  <option value="Approved">Approved</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 w-full">
              {loading ? (
                <div className="text-center text-gray-400 py-8">Loading...</div>
              ) : withdrawalRequests.length === 0 ? (
                <div className="text-center text-gray-400 py-8">
                  No {filterStatus.toLowerCase()} withdrawal requests found.
                </div>
              ) : (
                <div className="space-y-4">
                  {withdrawalRequests.map((request, index) => (
                    <div
                      key={index}
                      className="bg-gray-700 rounded-lg p-4 flex justify-between items-center"
                    >
                      <div>
                        <p className="text-white font-medium">User: {request.username}</p>
                        <p className="text-gray-400">Amount: {request.amount} birr</p>
                        <p className="text-gray-400">Date: {request.date}</p>
                      </div>
                      <div className="flex gap-2">
                        <button className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white">
                          Approve
                        </button>
                        <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-white">
                          Reject
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      case 'paymentSettings':
        return (
          <div className="bg-gray-800 rounded-lg p-6 min-w-3/4 m-auto" >
            <h2 className="text-xl font-semibold text-white mb-4">Payment Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Minimum Withdrawal Amount</label>
                <input
                  type="number"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter minimum amount"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Maximum Withdrawal Amount</label>
                <input
                  type="number"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter maximum amount"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Processing Fee (%)</label>
                <input
                  type="number"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter fee percentage"
                />
              </div>
              <button className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded text-white">
                Save Settings
              </button>
            </div>
          </div>
        );

      case 'manualDeposit':
        return (
          <div className="bg-gray-800 rounded-lg p-6 min-w-3/4 m-auto w-full">
            <h2 className="text-xl font-semibold text-white mb-4">Manual Deposit</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">User ID / Username</label>
                <input
                  type="text"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter user identifier"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Deposit Amount</label>
                <input
                  type="number"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter amount"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Reason / Note</label>
                <textarea
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  rows="3"
                  placeholder="Enter reason for manual deposit"
                />
              </div>
              <button className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded text-white">
                Process Deposit
              </button>
            </div>
          </div>
        );

      case 'manualWithdraw':
        return (
          <div className="rounded-lg min-w-3/4 m-auto w-full">
            <h2 className="text-xl font-semibold text-white mb-4">Manual Withdraw</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">User ID / Username</label>
                <input
                  type="text"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter user identifier"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Withdrawal Amount</label>
                <input
                  type="number"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  placeholder="Enter amount"
                />
              </div>
              <div>
                <label className="block text-gray-300 mb-2">Reason / Note</label>
                <textarea
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600"
                  rows="3"
                  placeholder="Enter reason for manual withdrawal"
                />
              </div>
              <button className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded text-white">
                Process Withdrawal
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6 w-full">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Payment Management</h1>

        {/* Tab Navigation */}
        <div className="flex space-x-1 mb-6 bg-gray-800 p-1 rounded-lg">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </div>
  );
};

export default Payments;
