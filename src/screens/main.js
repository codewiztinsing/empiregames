import React, { useState, useContext, useEffect } from 'react';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
const PlayingBoard = () => {
  const { selectBoard, playersLength } = useContext(BingoContext);

  const [board, setBoard] = useState(Array(5).fill().map(() => Array(5).fill(null)));
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [currentCall, setCurrentCall] = useState(null);
  const [winAmount, setWinAmount] = useState(0);
  const [betAmount, setBetAmount] = useState(0);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  useEffect(() => {
    socket.on('numberSelected', (number) => {
      setCurrentCall(number);
    });

    return () => {
      socket.off('numberSelected');
    };
  }, [socket]);

  const handleBingo = () => {
    // Add bingo validation logic here
    socket.emit('bingo');
  };

  const handleRefresh = () => {
    // Refresh board logic
    window.location.reload();
  };

  const handleLeave = () => {
    navigate('/');
  };

  return (
    <div className="game-container">
      <div className="stats-bar">
        <div className="stat-item">
          <span>Win</span>
          <span>{winAmount}</span>
        </div>
        <div className="stat-item">
          <span>Players</span>
          <span>{playersLength}</span>
        </div>
        <div className="stat-item">
          <span>Bet</span>
          <span>{betAmount}</span>
        </div>
        <div className="stat-item">
          <span>Call</span>
          <span>{currentCall}</span>
        </div>
      </div>

      <div className="bingo-content">

        <div className="called-numbers">
          <div className="called-numbers-grid">
            <div className="column">
              <div className="column-header">B</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'called' : ''}`}>
                  {i + 1}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">I</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'called' : ''}`}>
                  {i + 16}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">N</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'called' : ''}`}>
                  {i + 31}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">G</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 46) ? 'called' : ''}`}>
                  {i + 46}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">O</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 61) ? 'called' : ''}`}>
                  {i + 61}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="playing-section">

        <div> 
        <div className="current-call">
          <p>Current Call:</p>
          <div className="call-display">
  
                <span className="call-letter">
                 B
                </span>
                <span className="call-number">1</span>
             
          </div>
        </div>
        </div>


        <div className="bingo-header">
        <div className="bingo-letters">
          <span>B</span>
          <span>I</span>
          <span>N</span>
          <span>G</span>
          <span>O</span>
        </div>
      </div>

      <div className="bingo-board">
        {selectBoard.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row">
            {row.map((cell, colIndex) => (
              <div key={colIndex} className="board-cell">
                {cell}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="game-controls">
        <button className="bingo-button" onClick={handleBingo}>
          BINGO!
        </button>
        <div className="action-buttons">
          <button className="refresh-button" onClick={handleRefresh}>
            Refresh
          </button>
          <button className="leave-button" onClick={handleLeave}>
            Leave
          </button>
        </div>
      </div>

        </div>




    

      </div>

     
    </div>
  );
};

export default PlayingBoard;
