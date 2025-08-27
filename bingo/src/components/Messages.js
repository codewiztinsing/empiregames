import React, { useState } from 'react';
import { Send, MessageSquare, Users, Image } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

function Messages() {
  const [messageContent, setMessageContent] = useState('');
  const [includeImage, setIncludeImage] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleBroadcastMessage = async () => {
    if (!messageContent.trim()) {
      toast.error('Please enter a message content');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call for broadcasting message
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Message broadcasted successfully!');
      setMessageContent('');
      setIncludeImage(false);
    } catch (error) {
      toast.error('Failed to broadcast message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className='h-screen w-full overflow-y-auto'>
        <Toaster position="top-right" reverseOrder={false} />
        
        <div className="min-h-screen bg-gray-900 p-6 w-full">
          <div className="w-full max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Broadcast Message</h1>
                <p className="text-gray-400">Send a message to all users who have interacted with the Telegram bot. Messages will be delivered through the Telegram bot.</p>
              </div>
              <div className="bg-blue-600 p-3 rounded-lg">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
            </div>

            {/* Message Form */}
            <div className="bg-gray-800 rounded-xl p-6">
              <div className="mb-6">
                <label className="block text-white text-sm font-medium mb-3">
                  Message Content
                </label>
                <textarea
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  placeholder="Enter your message here. You can use HTML formatting (<b>bold</b>, <i>italic</i>, etc.)"
                  className="w-full h-32 bg-gray-700 text-white placeholder-gray-400 border border-gray-600 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Include Image Option */}
              <div className="mb-6">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeImage}
                    onChange={(e) => setIncludeImage(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-white text-sm">Include image with the message</span>
                </label>
              </div>

              {/* Broadcast Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleBroadcastMessage}
                  disabled={isLoading || !messageContent.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg flex items-center gap-2 transition-colors font-medium"
                >
                  {isLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Broadcasting...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Broadcast Message
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8">
              <div className="bg-gray-800 p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">Total Recipients</h3>
                  <div className="bg-green-600 p-2 rounded-lg">
                    <Users className="w-5 h-5 text-white" />
                  </div>
                </div>
                <p className="text-2xl font-bold text-green-400 mt-2">1,234</p>
                <p className="text-sm text-gray-400 mt-1">Active bot users</p>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">Messages Sent</h3>
                  <div className="bg-blue-600 p-2 rounded-lg">
                    <MessageSquare className="w-5 h-5 text-white" />
                  </div>
                </div>
                <p className="text-2xl font-bold text-blue-400 mt-2">567</p>
                <p className="text-sm text-gray-400 mt-1">This month</p>
              </div>

              <div className="bg-gray-800 p-6 rounded-xl">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">Delivery Rate</h3>
                  <div className="bg-purple-600 p-2 rounded-lg">
                    <Send className="w-5 h-5 text-white" />
                  </div>
                </div>
                <p className="text-2xl font-bold text-purple-400 mt-2">98.5%</p>
                <p className="text-sm text-gray-400 mt-1">Success rate</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Messages;
