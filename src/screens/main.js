import React, { useState, useContext, useEffect } from 'react';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
const PlayingBoard = () => {
  const { selectBoard, playersLength, countDown, roomId } = useContext(BingoContext);

  const [board, setBoard] = useState(Array(5).fill().map(() => Array(5).fill(null)));
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [currentCall, setCurrentCall] = useState(null);
  const [lastBall,setLastBall] = useState(0);
  const [winAmount, setWinAmount] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [selectedCell, setSelectedCell] = useState([]);
  // const [betAmount, setBetAmount] = useState(0);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  useEffect(() => {
    socket.on('numberSelected', (number) => {
      setCurrentCall(number);
    });

    if (lastBall) { 
      const element = document.getElementById(`${lastBall.letter}${lastBall.number}`);
      console.log("element",element,lastBall);
      if (element) {
        element.classList.add('called');
      }
    }


    return () => {
      socket.off('numberSelected');
    };
  }, [socket,lastBall,selectedCell]);

  const handleBingo = () => {
    // Add bingo validation logic here
    socket.emit('bingo');
  };

  function handleGameState(data) {
    // console.log("data in game")
    if (data.lastBall && data.lastBall.length > 0) {
      setLastBall(data.lastBall[data.lastBall.length - 1]);
    }
    setLastBall(data.lastBall)
    if(data.total_called_numbers){
      setTotalCalledNumbers(data.total_called_numbers)
    }
  
  }

  
  socket.on('gameState', handleGameState);

  const handleRefresh = () => {
    // Refresh board logic
    window.location.reload();
  };

  const handleLeave = () => {
    navigate('/');
  };

  const handleCellClick = (cell) => {
    setSelectedCell([...selectedCell, cell]);
   
  };

  return (
    <div className="game-container">
      <div className="stats-bar">
        <div className="stat-item">
          <span>Win</span>
          <span>{roomId * playersLength * 0.8}</span>
        </div>
        <div className="stat-item">
          <span>Players</span>
          <span>{playersLength}</span>
        </div>
        <div className="stat-item">
          <span>Bet</span>
          <span>{roomId}</span>
        </div>
        <div className="stat-item">
          <span>Call</span>
          <span>{totalCalledNumbers}</span>
        </div>
      </div>

      <div className="bingo-content">

        <div className="called-numbers">
          <div className="called-numbers-grid">
            <div className="column">
              <div className="column-header">B</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'called' : ''}`}
                id={`B${i + 1}`}
                
                >
                  {i + 1}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">I</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'called' : ''}`}
                id={`I${i + 16}`}
                
                >
                  {i + 16}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">N</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'called' : ''}`}
                id={`N${i + 31}`}
                
                >
                  {i + 31}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">G</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} 
                  className={`number ${calledNumbers?.includes(i + 46) ? 'called' : ''}`}
                  id={`G${i + 46}`}

                
                >
                  {i + 46}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">O</div>
              {Array.from({length: 15}, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 61) ? 'called' : ''}`}
                id={`O${i + 61}`}

                >
                  {i + 61}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="playing-section">

        <div> 
        <div className="current-call">
          {lastBall ? (
            <div className="ball-display">
              <div className="ball">
                {lastBall.combined}
              </div>
            </div>
          ) : (
            <div className="waiting-state">
              {countDown > 0 ? (
                <div>
                  <p>Game starting in:</p>
                  <div className="countdown">{countDown}</div>
                </div>
              ) : (
                <p>Game to start...</p>
              )}
            </div>
          )}

        
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
              <div key={colIndex} 
                className={`board-cell`}
                style={{ backgroundColor: selectedCell.includes(cell) ? '#4CAF50' : 'white' }}
                id={`${cell <= 15 && cell > 0 ? 'b' : cell <= 30 && cell > 15 ? 'i' : cell <= 45 && cell > 30 ? 'n' : cell <= 60 && cell > 45 ? 'g' : cell <= 75 && cell > 60 ? 'o' : ''}${cell}`}
                onClick={() => {
                  handleCellClick(cell);
                  setSelectedCell([...selectedCell, cell]);
                }}
              >
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
