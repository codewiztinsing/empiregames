import React, { useState, useEffect } from 'react';
import PaymentRequestModal from './PaymentRequestModal';
import { getWithdrawalRequests, getWithdrawalRequestsByTelegramId, getAutomaticDeposit } from "../services/api";

const Payments = () => {
  const [activeTab, setActiveTab] = useState('withdrawalRequests');
  const [filterStatus, setFilterStatus] = useState('Pending');
  const [withdrawalRequests, setWithdrawalRequests] = useState([]);
  const [automaticDeposit, setAutomaticDeposit] = useState([]);
  const [loading, setLoading] = useState(true); 
  const [isPaymentRequestModalOpen, setIsPaymentRequestModalOpen] = useState(false);
  const [telegramId, setTelegramId] = useState(null);
  const handleSubmitPaymentRequest = async (data) => {
    console.log("data", data);
  };

  useEffect(() => {
    fetchWithdrawalRequests();
    fetchAutomaticDeposit();
  }, []);

  const fetchWithdrawalRequests = async () => {
    console.log("fetching withdrawal requests")
    try {
      // Replace with actual API call:
      const response = await getWithdrawalRequests();
      console.log("response details", response.data)
      setWithdrawalRequests(response.data);
      
      setTelegramId(response.data.telegramId);
    } catch (error) {
      console.error('Error fetching withdrawal requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAutomaticDeposit = async () => {
    try {
      const response = await getAutomaticDeposit();
      console.log("automatic deposit response details", response.data)
      setAutomaticDeposit(response.data);
    } catch (error) {
      console.error('Error fetching automatic deposit:', error);
    } finally {
      setLoading(false);
    }
  }

  const openPaymentRequestDetails = (telegramId) => {
    setIsPaymentRequestModalOpen(true);
    setTelegramId(telegramId);
  };

  const tabs = [
    { id: 'withdrawalRequests', label: 'Withdrawal Requests' },
    { id: 'automaticDeposit', label: 'Automatic Deposit' },
    { id: 'paymentSettings', label: 'Payment Settings' },
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
                  {console.log("withdrawalRequests data", withdrawalRequests.data)}
                  {Array.isArray(withdrawalRequests.data) && withdrawalRequests.data.map((request, index) => (
                    <div
                      onClick={() => openPaymentRequestDetails(request.player.telegramId)}
                      key={index}
                      className="bg-gray-700 rounded-lg p-4 flex justify-between items-center"
                    >
                      <div >
                        <p className="text-white font-medium flex items-center gap-2">
                          <i className="fas fa-user"></i>
                          Phone: {request.player.phoneNumber}
                        </p>
                        <p className="text-gray-400 flex items-center gap-2">
                          <i className="fas fa-money-bill-wave"></i>
                          Amount: {request.amount} birr
                        </p>
                        <p className="text-gray-400 flex items-center gap-2">
                          <i className="fas fa-calendar-alt"></i>
                          Date: {request.updatedAt}
                        </p>
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

      case 'automaticDeposit':
        return (
          <div className="bg-gray-800 rounded-lg p-6 min-w-3/4 m-auto w-full">
            <h2 className="text-xl font-semibold text-white mb-4">Automatic Deposit</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 mb-2">Payment Sessions</label>
                <div className="bg-gray-700 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="space-y-3">
                  {console.log("payment request",automaticDeposit.data)}
                  {automaticDeposit.data.map((session, index) => (
                    <div key={index}>
                        {/* Payment Session Item */}
                    <div className="bg-gray-600 rounded-lg p-3 border border-gray-500">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="text-white font-medium">Session #{session.id}</h4>
                          <p className="text-gray-400 text-sm">User: {session.player.username}</p>
                        </div>
                        <span className={`px-2 py-1 text-white text-xs rounded ${
                          session.status === 'completed' ? 'bg-green-600' :
                          session.status === 'pending' ? 'bg-yellow-600' :
                          session.status === 'failed' ? 'bg-red-600' :
                          'bg-gray-600'
                        }`}>{session.status}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400">Amount:</p>
                          <p className="text-white font-medium">{session.amount} birr</p>
                        </div>
                        <div>
                          <p className="text-gray-400">Date:</p>
                          <p className="text-white">{session.createdAt}</p>
                        </div>
                      </div>
                    </div>
                    </div>
                  ))}
              
                  

                  
                  
                  </div>
                </div>
               
              </div>
              <button className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded text-white">
                Process Automatic Deposit
              </button>
            </div>
          </div>
        );

      
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
      <PaymentRequestModal
        isOpen={isPaymentRequestModalOpen}
        onClose={() => setIsPaymentRequestModalOpen(false)}
        onSubmit={handleSubmitPaymentRequest}
        telegramId={telegramId}
      />
    </div>
  );
};

export default Payments;
