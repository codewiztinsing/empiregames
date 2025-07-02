import React, { useState } from 'react';
import { SocketContext } from '../contexts/socket';
import { useContext } from 'react';
import './selections.css';
import { useEffect } from 'react';


const Selections = () => {
  const [selectedNumber, setSelectedNumber] = useState(null);
  const socket = useContext(SocketContext);
  console.log("socket", socket);

  
  // Generate numbers 1-100
  const numbers = Array.from({length: 100}, (_, i) => i + 1);

  // Generate 5x5 combination board for a number
  const generateCombination = (num) => {
    const combination = [];
    // Generate 5 rows
    for(let i = 0; i < 5; i++) {
      const row = [];
      // Generate 5 columns
      for(let j = 0; j < 5; j++) {
        // Generate unique random numbers for each cell
        let randomNum;
        do {
          randomNum = Math.floor(Math.random() * 100) + 1;
        } while(row.includes(randomNum));
        row.push(randomNum);
      }
      combination.push(row);
    }
    return combination;
  };

  const handleStartGame = () => {
    socket.emit('startGame');
  };

  const handleNumberClick = (number) => {
    setSelectedNumber(number);
  };

  return (
    <div className="selections-container">
      <div className="numbers-grid">
        {numbers.map(number => (
          <div 
            key={number}
            className={`number-cell ${selectedNumber === number ? 'selected' : ''}`}
            onClick={() => handleNumberClick(number)}
          >
            {number}
          </div>
        ))}
      </div>

      {selectedNumber && (
        <div className="combination-board">
         
          <div className="board-grid">
            {generateCombination(selectedNumber).map((row, rowIndex) => (
              <div key={rowIndex} className="board-row">
                {row.map((num, colIndex) => (
                  <div key={colIndex} className="board-cell">
                    {num}
                  </div>
                ))}
              </div>
            ))}
          </div>
          <button className="start-game-button" onClick={() => handleStartGame()}>Start Game</button>
        </div>
      )}

   
    </div>
  );
};

export default Selections;
