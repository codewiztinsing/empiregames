import React from 'react';

const gameTypes = [
  {
    id: 1,
    name: 'Classic Bingo',
    description: 'Traditional 5x5 bingo with standard patterns',
    price: 'ETB 10.00',
    players: '1-100',
    duration: '15-30 min',
    pattern: 'Line, Full House',
    difficulty: 'Easy',
    color: 'bg-blue-600'
  },
  {
    id: 2,
    name: 'Speed Bingo',
    description: 'Fast-paced bingo with quick number calls',
    price: 'ETB 15.00',
    players: '1-50',
    duration: '5-10 min',
    pattern: 'Any Line',
    difficulty: 'Medium',
    color: 'bg-green-600'
  },
  {
    id: 3,
    name: 'Pattern Bingo',
    description: 'Complete specific patterns to win',
    price: 'ETB 20.00',
    players: '1-75',
    duration: '20-40 min',
    pattern: 'Custom Patterns',
    difficulty: 'Hard',
    color: 'bg-purple-600'
  },
  {
    id: 4,
    name: 'Progressive Jackpot',
    description: 'Growing jackpot with multiple winners',
    price: 'ETB 25.00',
    players: '1-200',
    duration: '30-60 min',
    pattern: 'Full House',
    difficulty: 'Expert',
    color: 'bg-yellow-600'
  }
];

function GameTypes() {
  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Game Types</h1>
          <p className="text-gray-400">Choose your preferred bingo game style</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {gameTypes.map((game) => (
            <div key={game.id} className="bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
              <div className={`${game.color} p-4`}>
                <h3 className="text-xl font-bold text-white">{game.name}</h3>
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium mt-2 ${
                  game.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                  game.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                  game.difficulty === 'Hard' ? 'bg-orange-100 text-orange-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {game.difficulty}
                </span>
              </div>
              
              <div className="p-6">
                <p className="text-gray-300 mb-4 text-sm">{game.description}</p>
                
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Price:</span>
                    <span className="text-white font-semibold">{game.price}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Players:</span>
                    <span className="text-white">{game.players}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Duration:</span>
                    <span className="text-white">{game.duration}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400 text-sm">Pattern:</span>
                    <span className="text-white">{game.pattern}</span>
                  </div>
                </div>
                
                <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200">
                  Join Game
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-gray-800 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-white mb-4">How to Play</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-indigo-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-white font-bold text-lg">1</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Choose Game Type</h3>
              <p className="text-gray-400 text-sm">Select your preferred bingo game style and difficulty level</p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-white font-bold text-lg">2</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Get Your Card</h3>
              <p className="text-gray-400 text-sm">Receive your unique bingo card with random numbers</p>
            </div>
            
            <div className="text-center">
              <div className="bg-yellow-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-white font-bold text-lg">3</span>
              </div>
              <h3 className="text-white font-semibold mb-2">Mark & Win</h3>
              <p className="text-gray-400 text-sm">Mark called numbers and complete the winning pattern</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GameTypes;
