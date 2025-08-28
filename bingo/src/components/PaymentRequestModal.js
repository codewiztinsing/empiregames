import React, { useState, useEffect } from "react";
import {
  getWithdrawalRequestsByTelegramId,
  getPaymentSessionsByTelegramId,
  rejectWithdrawalRequest,
  approveWithdrawalRequest
} from "../services/api";
import { toast } from "react-toastify";

const PaymentRequestModal = ({ isOpen, onClose, telegramId }) => {
  const [paymentRequests, setPaymentRequests] = useState([]);
  const [paymentSessions, setPaymentSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("requests");

  useEffect(() => {
    if (isOpen && telegramId) {
      fetchPaymentDetails();
    }
  }, [isOpen, telegramId]);

  const fetchPaymentDetails = async () => {
    try {
      setLoading(true);
      const requestsResponse = await getWithdrawalRequestsByTelegramId(telegramId);
      console.log("request response data",requestsResponse.data.data)
      setPaymentRequests(requestsResponse?.data?.data || []);
      
    } catch (error) {
      console.error("Error fetching payment details:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case "pending":
        return "text-yellow-400";
      case "approved":
        return "text-green-400";
      case "rejected":
        return "text-red-400";
      case "completed":
        return "text-blue-400";
      default:
        return "text-gray-400";
    }
  };

  const handleApprove = async () => {
    try {
      const response = await approveWithdrawalRequest(paymentRequests.id);
      if (response.success) {
        toast.success("Withdrawal request approved successfully");
      } else {
        toast.error("Failed to approve withdrawal request");
      }
    } catch (error) {
      console.error("Error approving withdrawal request:", error);
    }
    
  }

  const handleReject = async () => {
    try {
      const response = await rejectWithdrawalRequest(paymentRequests.id);
      if (response.success) {
        toast.success("Withdrawal request rejected successfully");
      } else {
        toast.error("Failed to reject withdrawal request");
      }
    } catch (error) {
      console.error("Error rejecting withdrawal request:", error);
    }
    
  }

  const handleClose = () => {
    onClose();
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg w-full h-full max-w-none max-h-none overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-4 sm:p-6 border-b border-gray-700">
          <h2 className="text-lg sm:text-2xl font-bold text-white truncate pr-4">
            Payment Details - User: {telegramId}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl flex-shrink-0"
          >
            ×
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-4 sm:px-6 py-4 border-b border-gray-700">
          <div className="flex space-x-1 bg-gray-700 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab("requests")}
              className={`px-3 sm:px-4 py-2 rounded-md font-medium transition-colors text-sm sm:text-base ${
                activeTab === "requests"
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:text-white hover:bg-gray-600"
              }`}
            >
              Withdrawal Requests
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4 sm:p-6">
          {loading ? (
            <div className="text-center text-gray-400 py-8">Loading...</div>
          ) : (
            <div className="space-y-4 h-full">
              {/* Withdrawal Requests */}
              {activeTab === "requests" && (
                <div className="h-full flex flex-col">
                  <h3 className="text-base sm:text-lg font-semibold text-white mb-4">
                    Withdrawal Requests ({paymentRequests.length})
                  </h3>
                  {paymentRequests.length === 0 ? (
                    <div className="text-center text-gray-400 py-8 flex-1 flex items-center justify-center">
                      No withdrawal requests found for this user.
                    </div>
                  ) : (
                    <div className="space-y-3 flex-1 overflow-auto">
                     
                        <div
                          key={paymentRequests.id}
                          className="bg-gray-700 rounded-lg p-3 sm:p-4 shadow"
                        >
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                            <div>
                              <p className="text-gray-400 text-xs sm:text-sm">Amount</p>
                              <p className="text-white font-medium text-sm sm:text-base">
                                {paymentRequests.amount} birr
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400 text-xs sm:text-sm">Status</p>
                              <p
                                className={`font-medium text-sm sm:text-base ${getStatusColor(
                                  paymentRequests.status
                                )}`}
                              >
                                {paymentRequests.status || "Pending"}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400 text-xs sm:text-sm">Created</p>
                              <p className="text-white text-xs sm:text-sm">
                                {formatDate(paymentRequests.createdAt)}
                              </p>
                            </div>

                            <div>
                              <p className="text-gray-400 text-xs sm:text-sm">CBE Acc no</p>
                              <p className="text-white text-xs sm:text-sm">
                                {paymentRequests.accountNumber}
                              </p>
                            </div>

                          
                            <div>
                              <p className="text-gray-400 text-xs sm:text-sm">Updated</p>
                              <p className="text-white text-xs sm:text-sm">
                                {formatDate(paymentRequests.updatedAt)}
                              </p>
                            </div>
                          </div>
                          {paymentRequests.note && (
                            <div className="mt-3">
                              <p className="text-gray-400 text-xs sm:text-sm">Note</p>
                              <p className="text-white text-sm sm:text-base">{paymentRequests.note}</p>
                            </div>
                          )}
                        </div>

                      {/* Player Details Section */}
                      <div className="bg-gray-600 rounded-lg p-3 sm:p-4">
                        <h4 className="text-base sm:text-lg font-semibold text-white mb-3">Player Details</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                          <div>
                            <p className="text-gray-400 text-xs sm:text-sm">Telegram ID</p>
                            <p className="text-white font-medium text-sm sm:text-base break-all">{telegramId}</p>
                          </div>
                          
                          <div>
                            <p className="text-gray-400 text-xs sm:text-sm">Username</p>
                            <p className="text-white font-medium text-sm sm:text-base">
                              {paymentRequests?.player?.username || "N/A"}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-400 text-xs sm:text-sm">Phone Number</p>
                            <p className="text-white font-medium text-sm sm:text-base">
                              {paymentRequests?.player?.phoneNumber || "N/A"}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Games Played Section */}
                      <div className="bg-gray-600 rounded-lg p-3 sm:p-4">
                        <h4 className="text-base sm:text-lg font-semibold text-white mb-3">Recent Games Played</h4>
                        <div className="space-y-2 max-h-32 sm:max-h-48 overflow-y-auto">
                          {/* Placeholder for games - this would come from API */}
                         
                          {paymentRequests?.player?.games?.map((game) => (
                          <div className="bg-gray-700 rounded p-2 sm:p-3">
                            <div className="flex justify-between items-center">
                              <div>
                                <p className="text-white font-medium text-sm sm:text-base">Bingo Game #{game.id}</p>
                                <p className="text-gray-400 text-xs sm:text-sm">Played {game.createdAt}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-red-400 font-medium text-sm sm:text-base">-{game.betAmount} birr</p>
                                <p className="text-gray-400 text-xs sm:text-sm">Participant</p>
                              </div>
                            </div>
                          </div>
                          ))}
                        </div>
                
                      </div>
                      
                    </div>
                  )}
                </div>
              )}

              
            </div>
          )}
        </div>

        {/* Footer */}

        <div className="border-t border-gray-700 p-4 sm:p-6 flex gap-2">
          <div className="flex justify-end gap-2">
            <button
              onClick={handleReject}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm sm:text-base"
            >
              Reject
            </button>
            <button
              onClick={handleApprove}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded text-sm sm:text-base"
            >
              Approve
            </button>
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm sm:text-base"
            >
              Close
            </button>
          </div>
        </div>

     

      </div>
    </div>
  );
};

export default PaymentRequestModal;
