import React from 'react';
import './BingoCard.css';

const BINGO_LETTERS = ['B', 'I', 'N', 'G', 'O'];

function BingoCard({ card, calledNumbers, onBingo }) {
  const checkBingo = () => {
    // Check for standard bingo (5 in a row, column, or diagonal)
    // This can be expanded for other patterns
    
    // Check rows
    for (let row = 0; row < 5; row++) {
      if (card[row].every(cell => cell.marked || cell.number === 'FREE')) {
        onBingo();
        return;
      }
    }
    
    // Check columns
    for (let col = 0; col < 5; col++) {
      if (card.every(row => row[col].marked || row[col].number === 'FREE')) {
        onBingo();
        return;
      }
    }
    
    // Check diagonals
    if (
      [card[0][0], card[1][1], card[2][2], card[3][3], card[4][4]
    ].every(cell => cell.marked || cell.number === 'FREE')) {
      onBingo();
      return;
    }
    
    if (
      [card[0][4], card[1][3], card[2][2], card[3][1], card[4][0]
    ].every(cell => cell.marked || cell.number === 'FREE')) {
      onBingo();
      return;
    }
  };

  // Auto-mark called numbers
  const markedCard = card.map(row => 
    row.map(cell => ({
      ...cell,
      marked: calledNumbers.includes(cell.number) || cell.number === 'FREE'
    }))
  );

  // Check for bingo whenever calledNumbers changes
  React.useEffect(() => {
    checkBingo();
  }, [calledNumbers]);

  return (
    <div className="bingo-card">
      <div className="bingo-header">
        {BINGO_LETTERS.map(letter => (
          <div key={letter} className="bingo-header-cell">{letter}</div>
        ))}
      </div>
      {markedCard.map((row, rowIndex) => (
        <div key={rowIndex} className="bingo-row">
          {row.map((cell, colIndex) => (
            <div 
              key={`${rowIndex}-${colIndex}`} 
              className={`bingo-cell ${cell.marked ? 'marked' : ''} ${cell.number === 'FREE' ? 'free' : ''}`}
            >
              {cell.number}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default BingoCard;