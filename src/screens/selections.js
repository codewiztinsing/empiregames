import React, { useState, useEffect, useContext, useCallback } from 'react';
import { SocketContext } from '../contexts/socket';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';

const Selections = () => {
  const { selectedNumber, setSelectedNumber, setSelectBoard, gameId } = useContext(BingoContext);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();
  const [playerId, setPlayerId] = useState(null);
  const [pickedNumbers, setPickedNumbers] = useState([]);
  const { playersLength, setPlayersLength } = useContext(BingoContext);
  const [isLoading, setIsLoading] = useState(false);

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 100 }, (_, i) => i + 1);

  // Get playerId from URL once on mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    setPlayerId(queryParams.get('playerId'));
  }, []);

  // Socket listeners with cleanup
  useEffect(() => {
    const handleGameState = (state) => {
      console.log('Received updated game state:', state);
      setPickedNumbers(state.pickedNumbers);
      setPlayersLength(state.total_players);
    };
    // socket.on('pickedNumbers', handlePickedNumbers);
    socket.on('gameState', handleGameState);
    return () => {
      // socket.off('pickedNumbers', handlePickedNumbers);
      socket.off('gameState', handleGameState);
    };
  }, [socket, gameId]);

  // Memoized board generation
  const generateCombination = useCallback(() => {
    const card = [];
    const ranges = [
      [1, 15],    // B
      [16, 30],   // I
      [31, 45],   // N
      [46, 60],   // G
      [61, 75],   // O
    ];

    for (let col = 0; col < 5; col++) {
      const nums = [];
      for (let n = ranges[col][0]; n <= ranges[col][1]; n++) {
        nums.push(n);
      }
      
      for (let row = 0; row < 5; row++) {
        if (!card[row]) card[row] = [];
        if (col === 2 && row === 2) {
          card[row][col] = '*';
        } else {
          const idx = Math.floor(Math.random() * nums.length);
          card[row][col] = nums.splice(idx, 1)[0];
        }
      }
    }
    return card;
  }, []);

  const handleStartGame = async () => {
    if (!selectedNumber || !playerId || !gameId) return;
    setIsLoading(true);
    try {
      socket.emit('joinGame', { playerId, gameId,selectedNumber })
      navigate('/play');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNumberClick = (number) => {
    if (pickedNumbers.includes(number)) return;
    
    const newBoard = generateCombination();
    setSelectedNumber(number);
    setSelectBoard(newBoard);
  };


  socket.on('gameState', (state) => {
    console.log('Received updated game state:', state);
    setPickedNumbers(state.pickedNumbers);
    setPlayersLength(state.total_players);
  });

  return (
    <div className="selections-container">
      
      <div className="numbers-grid">
        {numbers.map(number => {
          const isPicked = pickedNumbers.includes(number);
          const isSelected = selectedNumber === number;
          
          return (
            <button
              key={number}
              className={`number-cell 
                ${isPicked ? 'picked' : ''}
                ${isSelected ? 'selected' : ''}
              `}
              onClick={() => handleNumberClick(number)}
              disabled={isPicked}
              aria-label={isPicked ? `Number ${number} already picked` : `Select number ${number}`}
            >
              {number}
              {isPicked && <span className="picked-badge">Picked</span>}
            </button>
          );
        })}
      </div>

      {selectedNumber && (
        <div className="combination-board">
         
          <div className="board-grid">
            {generateCombination().map((row, rowIndex) => (
              <div key={rowIndex} className="board-row">
                {row.map((num, colIndex) => (
                  <div 
                    key={colIndex} 
                    className={`board-cell ${
                      pickedNumbers.includes(num) ? 'picked-on-board' : ''
                    }`}
                  >
                    {num}
                    {pickedNumbers.includes(num) && (
                      <span className="picked-indicator">✓</span>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
          <button
            className="start-game-button"
            onClick={handleStartGame}
            disabled={!selectedNumber || isLoading}
          >
            {isLoading ? 'Starting...' : 'Start Game'}
          </button>
        </div>
      )}
    </div>
  );
};

export default Selections;