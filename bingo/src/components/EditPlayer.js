import React, { useState, useEffect } from 'react';
import { X, Save, User, Mail, Phone, Calendar, Shield } from 'lucide-react';
import { getUser, updateUser } from '../services/api';
import toast from 'react-hot-toast';
import { Toaster } from 'react-hot-toast';
const EditPlayer = ({ playerId, username, phoneNumber, balance, status, onClose, onSave }) => {
  const [playerData, setPlayerData] = useState({
    username: username,
    phone: phoneNumber,
    balance: balance,
    status: status
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    console.log("playerId",playerId);
    if (playerId) {
      fetchPlayerData();
    }
  }, [playerId]);

  const fetchPlayerData = async () => {
    console.log("playerId",playerId);
    try {
      setLoading(true);
      const response = await getUser(playerId);
      console.log("response.data",response.data);
      setPlayerData(response.data);
    } catch (error) {
      console.error('Error fetching player data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPlayerData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    console.log("playerData",playerData);
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      // Here you would typically call an update API endpoint
      const response =  await updateUser(playerId, playerData);
      if(response.status === 200){
        console.log("status code",response.status);
        // onSave(response.data);
        toast.success("Player updated successfully");
      }else{
        console.log("Error updating player:", response.data);
        toast.error("Error updating player:", response.data);
      }
      onClose();
    } catch (error) {
      console.error('Error updating player:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    <Toaster />
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <User className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold text-white">
              {playerId ? 'Edit Player' : 'Add New Player'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Personal Information */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Personal Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            

              
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Username *
                </label>
                <input
                  type="text"
                  name="username"
                  value={playerData.username}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 ${
                    errors.username ? 'border-red-500' : 'border-gray-600'
                  }`}
                  placeholder={`${playerData.username}`}
                />
                {errors.username && (
                  <p className="text-red-400 text-sm mt-1">{errors.username}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Telegram ID 
                </label>
                <input
                  type="text"
                  name="telegramId"
                  value={playerData.telegramId}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 ${
                    errors.telegramId ? 'border-red-500' : 'border-gray-600'
                  }`}
                />
                {errors.telegramId && (
                  <p className="text-red-400 text-sm mt-1">{errors.telegramId}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Phone className="w-4 h-4 inline mr-2" />
                  Phone *
                </label>
                <input
                  type="number"
                  name="phone"
                  value={playerData.phone}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 ${
                    errors.phone ? 'border-red-500' : 'border-gray-600'
                  }`}
                  placeholder={`${playerData.phone}`}
                />
                {errors.phone && (
                  <p className="text-red-400 text-sm mt-1">{errors.phone}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Phone className="w-4 h-4 inline mr-2" />
                  Balance
                </label>
                <input
                  type="number"
                  name="balance"
                  value={playerData.balance}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-gray-700 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 ${
                    errors.balance ? 'border-red-500' : 'border-gray-600'
                  }`}
                />
                {errors.balance && (
                  <p className="text-red-400 text-sm mt-1">{errors.balance}</p>
                )}
              </div>
              
            </div>

          </div>

          {/* Additional Information */}
          

         

          {/* Action Buttons */}
          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              <Save className="w-5 h-5" />
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
    </>
  );
};

export default EditPlayer;
