import React from 'react';
import './BingoWinner.css';

const BingoWinner = () => {
  // Generate random numbers for each column within their respective ranges
  const generateRandomCard = () => {
    const card = [];
    const usedNumbers = new Set();

    for (let i = 0; i < 5; i++) {
      const row = [];
      for (let j = 0; j < 5; j++) {
        let min = j * 15 + 1;
        let max = (j + 1) * 15;
        let num;
        
        // Center square is always FREE
        if (i === 2 && j === 2) {
          num = 'FREE';
        } else {
          do {
            num = Math.floor(Math.random() * (max - min + 1)) + min;
          } while (usedNumbers.has(num));
          usedNumbers.add(num);
        }
        
        row.push({
          number: num,
          marked: num === 'FREE'
        });
      }
      card.push(row);
    }
    return card;
  };

  const bingoCard = generateRandomCard();

  return (
    <div className="bingo-card">
      {bingoCard.map((row, rowIndex) => (
        row.map((cell, colIndex) => (
          <div
            key={`${rowIndex}-${colIndex}`}
            className={`bingo-cell ${cell.marked ? 'marked' : ''}`}
          >
            {cell.number}
          </div>
        ))
      ))}
    </div>
  );
};

export default BingoWinner;
