import React from 'react';

const gameTypes = [
  {
    id: 1,
    name: 'Classic Bingo 75 Ball',
    description: 'Traditional 5x5 bingo with standard patterns',
    price: 'ETB 10.00',
    players: '1-400',
    duration: '5-15 min',
    pattern: 'Any Line, Full House',
    difficulty: 'Beginner',
    color: 'bg-blue-600'
  },
  {
    id: 2,
    name: 'Classic Bingo 75 Ball',
    description: 'Traditional 5x5 bingo with standard patterns',
    price: 'ETB 20.00',
    players: '1-400',
    duration: '5-15 min',
    pattern: 'Any Line, Full House',
    difficulty: 'Intermediate',
    color: 'bg-green-600'
  },
  {
    id: 3,
    name: 'Classic Bingo 75 Ball',
    description: 'Traditional 5x5 bingo with standard patterns',
    price: 'ETB 50.00',
    players: '1-400',
    duration: '5-15 min',
    pattern: 'Any Line, Full House',
    difficulty: 'Advanced',
    color: 'bg-purple-600'
  },
  {
    id: 4,
    name: 'Classic Bingo 75 Ball',
    description: 'Traditional 5x5 bingo with standard patterns',
    price: 'ETB 100.00',
    players: '1-400',
    duration: '5-15 min',
    pattern: 'Any Line, Full House',
    difficulty: 'Professional',
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
                
               
              </div>
            </div>
          ))}
        </div>

      
      </div>
    </div>
  );
}

export default GameTypes;
