import React, { useState } from 'react';
import { RefreshCw, Save } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

function BingoCard() {
  const [cards, setCards] = useState([
    '1,9,27,55,61,24,45,18,33,58,76,12,30,free,54,74,22,24,45,47,66,15,22,74,59,64',
    '14,30,35,60,7,9,19,35,52,70,3,18,free,59,73,6,25,36,50,69,5,11,52,64,73',
    '4,19,28,57,69,25,2,17,48,37,61,15,29,free,46,83,2,28,31,53,70,1,15,21,64',
    '8,7,25,49,49,73,20,45,74,3,27,19,free,51,62,1,22,25,50,69,5,13,24,44,66',
    '11,29,35,53,70,16,3,45,70,74,6,29,free,49,73,16,23,32,56,63,10,16,22,44,60',
    '6,3,19,45,70,73,15,17,39,51,71,8,20,free,54,63,4,25,41,52,66,12,18,34,69,68',
    '7,3,21,51,61,69,13,24,42,67,2,20,free,56,69,1,22,30,53,67,6,16,34,66,75',
    '8,3,29,59,55,64,10,26,37,45,74,7,21,free,54,67,9,19,51,58,65,15,19,35,59,73',
    '9,6,21,51,54,66,2,23,36,57,69,3,30,free,56,71,7,24,43,59,65,6,26,33,59,75',
    '10,9,26,57,49,68,14,29,44,46,67,6,27,free,68,72,10,26,45,54,62,8,22,43,58,66'
  ]);

  const [newCard, setNewCard] = useState('');

  const handleReset = () => {
    // Reset to default cards
    setCards([
      '1,9,27,55,61,24,45,18,33,58,76,12,30,free,54,74,22,24,45,47,66,15,22,74,59,64',
      '14,30,35,60,7,9,19,35,52,70,3,18,free,59,73,6,25,36,50,69,5,11,52,64,73',
      '4,19,28,57,69,25,2,17,48,37,61,15,29,free,46,83,2,28,31,53,70,1,15,21,64',
      '8,7,25,49,49,73,20,45,74,3,27,19,free,51,62,1,22,25,50,69,5,13,24,44,66',
      '11,29,35,53,70,16,3,45,70,74,6,29,free,49,73,16,23,32,56,63,10,16,22,44,60',
      '6,3,19,45,70,73,15,17,39,51,71,8,20,free,54,63,4,25,41,52,66,12,18,34,69,68',
      '7,3,21,51,61,69,13,24,42,67,2,20,free,56,69,1,22,30,53,67,6,16,34,66,75',
      '8,3,29,59,55,64,10,26,37,45,74,7,21,free,54,67,9,19,51,58,65,15,19,35,59,73',
      '9,6,21,51,54,66,2,23,36,57,69,3,30,free,56,71,7,24,43,59,65,6,26,33,59,75',
      '10,9,26,57,49,68,14,29,44,46,67,6,27,free,68,72,10,26,45,54,62,8,22,43,58,66'
    ]);
    toast.success('Cards reset to default');
  };

  const handleSaveCards = () => {
    // Save cards to localStorage or send to API
    localStorage.setItem('bingoCards', JSON.stringify(cards));
    toast.success('Cards saved successfully!');
  };

  const handleAddCard = () => {
    if (!newCard.trim()) {
      toast.error('Please enter card data');
      return;
    }
    
    // Validate card format (should have exactly 25 numbers/free)
    const cardNumbers = newCard.split(',');
    if (cardNumbers.length !== 25) {
      toast.error('Card must contain exactly 25 numbers (including "free")');
      return;
    }
    
    setCards([...cards, newCard]);
    setNewCard('');
    toast.success('New card added successfully!');
  };

  const handleDeleteCard = (index) => {
    const updatedCards = cards.filter((_, i) => i !== index);
    setCards(updatedCards);
    toast.success('Card deleted successfully!');
  };

  return (
    <>
      <div className='h-screen w-full overflow-y-auto'>
        <Toaster position="top-right" reverseOrder={false} />
        
        <div className="min-h-screen bg-gray-900 p-6 w-full">
          <div className="w-full max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Bingo Cards Management</h1>
                <p className="text-gray-400">Manage your bingo cards by entering them in the format below. Each line represents one card.</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleReset}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reset
                </button>
                <button
                  onClick={handleSaveCards}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
                >
                  <Save className="w-4 h-4" />
                  Save Cards
                </button>
              </div>
            </div>

            {/* Format Information */}
            <div className="bg-gray-800 p-4 rounded-lg mb-6">
              <p className="text-gray-300 text-sm mb-2">
                <strong>Format:</strong> <span className="text-blue-400">col1,number,number,... col2,number,representing a 5x5 grid</span>
              </p>
              <p className="text-gray-300 text-sm mb-2">
                <strong>Example:</strong> <span className="text-green-400">1,9,27,55,61,24,45,18,33,58,76,12,30,free,54,74,22,24,45,47,66,15,22,74,59,64</span>
              </p>
              <p className="text-yellow-400 text-sm">
                <strong>Note:</strong> Each card must have exactly 25 numbers (including "free" in the center).
              </p>
            </div>

            {/* Add New Card */}
            <div className="bg-gray-800 p-6 rounded-lg mb-6">
              <h3 className="text-xl font-semibold text-white mb-4">Add New Card</h3>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={newCard}
                  onChange={(e) => setNewCard(e.target.value)}
                  placeholder="Enter card data (comma-separated numbers)"
                  className="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                />
                <button
                  onClick={handleAddCard}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  Add Card
                </button>
              </div>
            </div>

            {/* Cards Data */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Cards Data</h3>
              <div className="space-y-3">
                {cards.map((card, index) => (
                  <div key={index} className="bg-gray-700 p-4 rounded-lg flex items-center justify-between">
                    <div className="flex-1">
                      <span className="text-gray-300 font-mono text-sm break-all">{card}</span>
                    </div>
                    <button
                      onClick={() => handleDeleteCard(index)}
                      className="ml-4 bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
              
              {cards.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-400">No bingo cards found. Add some cards above.</p>
                </div>
              )}
            </div>

            {/* Statistics */}
            <div className="mt-6 bg-gray-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-white mb-4">Statistics</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-gray-300 text-sm">Total Cards</p>
                  <p className="text-2xl font-bold text-blue-400">{cards.length}</p>
                </div>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-gray-300 text-sm">Valid Format</p>
                  <p className="text-2xl font-bold text-green-400">
                    {cards.filter(card => card.split(',').length === 25).length}
                  </p>
                </div>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <p className="text-gray-300 text-sm">Invalid Format</p>
                  <p className="text-2xl font-bold text-red-400">
                    {cards.filter(card => card.split(',').length !== 25).length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default BingoCard;
