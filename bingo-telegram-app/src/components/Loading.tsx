import React from 'react';

const Loading: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
      <div className="text-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin mx-auto" style={{ animationDelay: '0.1s' }}></div>
        </div>
        <h2 className="text-xl font-semibold text-white mb-2">Loading Bingo Game</h2>
        <p className="text-gray-300">Please wait while we set up your game...</p>
      </div>
    </div>
  );
};

export default Loading;
