import React, { useState, useContext, useEffect, use } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import BingoWinner from '../components/BingoWinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';




const PlayingBoard = () => {
  const {
    selectedNumber,
    selectedNumber2,
    selectBoard,
    selectBoard2,
    playersLength,
    countDown,
    setCountDown,
    roomId,
    playerId,
    gameId,
    setGameId,
    setToast,
    setIsToast,
    playerName,
  } = useContext(BingoContext);

  const [calledNumbers, setCalledNumbers] = useState([]);
  const [lastBall, setLastBall] = useState(null);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [selectedCell, setSelectedCell] = useState(new Set());
  const [isBingo, setIsBingo] = useState(false);
  const [winningCard, setWinningCard] = useState([]);
  const [recentCalledNumbers, setRecentCalledNumbers] = useState(['*', '*', '*']);
  const [winner, setWinner] = useState('');
  const [winnerCardNumber, setWinnerCardNumber] = useState(0);
  const [winnerPlayerName, setWinnerPlayerName] = useState('');
  const [firstBoardLost, setFirstBoardLost] = useState(false);
  const [secondBoardLost, setSecondBoardLost] = useState(false);

  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // ✅ Socket event bindings
  useEffect(() => {
    if (!socket) return;

    const handleGameState = (data) => {
      const calledNumber = data?.lastBall?.combined.split("-")[1]
      console.log("calledNumber",calledNumber)
      if(calledNumber){
        calledNumbers.push(parseInt(calledNumber))
        setCalledNumbers(calledNumbers)
      }
      setLastBall(data.lastBall);
      if (data.total_called_numbers) setTotalCalledNumbers(data.total_called_numbers);
      if (data.count_down) setCountDown(data.count_down);
      setGameId(data.gameId);
    };

    const handleFalseBingo = (data) => {
      const loserBoard = data.losser_board;
      if (loserBoard === selectedNumber) setFirstBoardLost(true);
      if (loserBoard === selectedNumber2) setSecondBoardLost(true);
    };

    const handleGameOver = (data) => {
      if (data.roomId === roomId) {
        navigate(`/?playerId=${playerId}&&betAmount=${roomId}&playerName=${playerName}`);
      }
    };

    const handleWinBingo = (data) => {
      if (data.winningCard) {
        setWinningCard(data.markedCells);
        setIsBingo(data.isBingo);
        setWinner(data.playerId);
        setWinnerCardNumber(data.winner_Number);
        setWinnerPlayerName(data.playerName);
      }
    };

    const handleJoinError = (data) => {
      if (data.roomId === roomId) {
        setToast(data.message);
        setIsToast(true);
        navigate(`/selection?playerId=${playerId}&betAmount=${roomId}`);
      }
    };

    const handlePlayerLeft = (data) => {
      if (data.playerId === playerId) {
        navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
        window.location.reload();
      }
    };

    socket.on('numberSelected', (number) => setLastBall(number));
    socket.on('gameState', handleGameState);
    socket.on('gameOver', handleGameOver);
    socket.on('winBingo', handleWinBingo);
    socket.on('falseBingo', handleFalseBingo);
    socket.on('joinError', handleJoinError);
    socket.on('playerLeft', handlePlayerLeft);

    socket.on('disconnect', () => {
      console.log('Client disconnected from server');
      handleLeave('disconnect');
    });

    return () => {
      socket.off('numberSelected');
      socket.off('gameState', handleGameState);
      socket.off('gameOver', handleGameOver);
      socket.off('winBingo', handleWinBingo);
      socket.off('falseBingo', handleFalseBingo);
      socket.off('joinError', handleJoinError);
      socket.off('playerLeft', handlePlayerLeft);
      socket.off('disconnect');
    };
  }, [socket, roomId, playerId, playerName, selectedNumber, selectedNumber2, setCountDown, setGameId, setToast, setIsToast, navigate]);

  // ✅ Track recent balls
  useEffect(() => {
    if (!lastBall) return;
    const recentBall = `${lastBall.letter}${lastBall.number}`;
    setRecentCalledNumbers((prev) => {
      const updated = [...prev, recentBall];
      return updated.length > 3 ? updated.slice(1) : updated;
    });
  }, [lastBall]);

  const handleBingo = (board, boardNumber) => {
    if (totalCalledNumbers === 0) {
      toast.error('Game is not started yet');
      return;
    }
    socket.emit('bingo', {
      gameId,
      roomId,
      playerId,
      markedCells: Array.from(selectedCell),
      playerName,
      board,
      boardNumber,
    });
  };

  const handleRefresh = () => {
    socket.emit('handleRefresh', { gameId, roomId, playerId });
  };

  const handleLeave = (reason) => {
    socket.emit('leave', { playerId, roomId, selectedNumber, selectedNumber2, reason });
  };

  const handleCellClick = (cell) => {
    setSelectedCell((prev) => {
      const updated = new Set(prev);
      if (updated.has(cell)) updated.delete(cell);
      else updated.add(cell);
      return new Set(updated);
    });
  };

  const handleCloseWinner = () => {
    setIsBingo(false);
    navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
  };

  return (
    <div className="game-container">
      <Toaster />

  {isBingo && (
  <div className="bingo-winner-overlay">
    <div className="bingo-winner-card">
      <div className="winner-card-header">
        <p className='winner-card-header-text'>Bingo Winner!</p>
      </div>

      <p className='winner-card-header-winner-number' style={{
        color: "green",
        fontSize: "1.6rem",
        fontWeight: "bold"
      }}>አሸናፊ ካርድ ቁጥር : {winnerCardNumber}</p>
      <p className='winner-card-header-text' style={{
          color: "green",
        fontSize: "1.6rem",
        fontWeight: "bold"
      }}>ስም : {winnerPlayerName},is Winner</p>


      <div className="winning-card">
        <div className="winning-card-row">
          {["B", "I", "N", "G", "O"].map((letter, index) => (
            <div key={index} className="winning-card-cell">
              <span>{letter}</span>
            </div>
          ))}
        </div>

        {winningCard[0].map((_, colIndex) => {
          const isColumnComplete = winningCard.every(row => row[colIndex].marked);
          const isRowComplete = winningCard[colIndex].every(cell => cell.marked);
          const isDiagonalComplete = winningCard.every((row, i) => row[i].marked);
          const isReverseDiagonalComplete = winningCard.every((row, i) => row[4-i].marked);
          const isFourCornersComplete = winningCard[0][0].marked && winningCard[0][4].marked && 
                                      winningCard[4][0].marked && winningCard[4][4].marked;
          const isFourEdgesComplete = winningCard[0][2].marked && winningCard[2][0].marked &&
                                    winningCard[2][4].marked && winningCard[4][2].marked;

          return (
            <div key={colIndex} className="winning-card-row">
              {winningCard.map((row, rowIndex) => (
                <div
                  key={rowIndex}
                  className="winning-card-cell"
                  style={{
                    backgroundColor: isRowComplete || isColumnComplete || isDiagonalComplete || isReverseDiagonalComplete || isFourCornersComplete || isFourEdgesComplete
                      ? 'green'
                      : row[colIndex].marked
                    
                      ? 'red'
                      : 'white',
                  }}
                >
                  <span>{row[colIndex].number}</span>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      <div className="choosen-numbers">
        <span className="choosen-number">የካርቴላ ቁጥር :- {winnerCardNumber}</span>
        <button className="close-winner-button" onClick={handleCloseWinner}>
          <p>Close</p>
        </button>
      </div>
    </div>
  </div>
)}


      <div className="stats-bar">
        <div className="stat-item">
          <span>ደራሽ</span>
          <span>{roomId * playersLength * 0.8}</span>
        </div>
        <div className="stat-item">
          <span>ብዛት</span>
          
          <span>{playersLength}</span>
        </div>
        <div className="stat-item">
          <span>መደብ </span>
        
          <span>{roomId}</span>
        </div>
        <div className="stat-item">
          <span>ጥሪ </span>
          <span>{totalCalledNumbers}</span>
        </div>


        <div className="stat-item">
          <span>ድምጽ </span>
          <select className='language-select'>
            <option value="1">Amh</option>
            <option value="3">Oromo</option>
            <option value="4">Tigrigna</option>
          </select>
        </div>
      </div>

<div className='middle-container'>
<div className="called-numbers">
        
        <div className="called-numbers-grid" style={{
          gap:"2px"
        }}>
          
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "rgb(202, 83, 83)",
              color: "white"
            }}>B</div>
            {Array.from({ length: 15 }, (_, i) => (
              <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'called' : ''} ${selectedNumber == i + 1 ? 'selected' : ''}`}
                id={`B${i + 1}`}

              >
                {i + 1}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "rgb(247, 190, 3)",
              color: "white"
            }}>I</div>
            {Array.from({ length: 15 }, (_, i) => (
            <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'called' : ''} ${selectedNumber == i + 16 ? 'selected' : ''}`}
                id={`I${i + 16}`}

              >
                {i + 16}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "rgb(50, 14, 150)",
              color: "white"
            }}>N</div>
            {Array.from({ length: 15 }, (_, i) => (
            <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'called' : ''} ${selectedNumber == i + 31 ? 'selected' : ''}`}
                id={`N${i + 31}`}

              >
                {i + 31}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "rgb(29, 160, 12)",
              color: "white"
            }}>G</div>
            {Array.from({ length: 15 }, (_, i) => (
              <div key={i}
                className={`number ${calledNumbers?.includes(i + 46) ? 'called' : ''} ${selectedNumber == i + 46 ? 'selected' : ''}`}
                id={`G${i + 46}`}
              >
                {i + 46}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "rgb(148, 17, 137)",
              color: "white"
            }}>O</div>
            {Array.from({ length: 15 }, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 61) ? 'called' : ''} ${selectedNumber == i + 61 ? 'selected' : ''}  `}
                id={`O${i + 61}`}

              >
                {i + 61}
              </div>
            ))}
          </div>
        </div>
        <div className="action-buttons">
              <button className="refresh-button" onClick={handleRefresh}>
                Refresh
              </button>
              <button className="leave-button" onClick={() => handleLeave("leave")}>
                Leave
              </button>
      </div>

      </div>

      

      <div className="bingo-content">

  
        <div className="playing-section">

          <div>
            <div className="current-call">
       
              {lastBall ? (
                <div className="ball-display">
                  <div className='outer-circle'>

                    <div  className='inner-circle'>

                    <div className="ball">
                    {lastBall.combined}
                  </div>

                    </div>

                  </div>
              
                
                </div>
              ) : (
                <div className="waiting-state">
               
                </div>
              )}
            </div>
          </div>

          

          <div className="recent-called-numbers-container">
              {countDown > 0  && countDown != 29 ? (
                // Show countdown when greater than 0
                <div className='game-starting-container'>
                  <p className='game-starting'>00</p>
                  <p className='game-starting'>:</p>
                  <p className='game-countdown'>{countDown}</p>
                </div>
              ) : countDown === 0 ? (
                <div className="recent-called-numbers">
                  <div className="recent-called-numbers-grid">
                    {recentCalledNumbers.map((number, index) => (
                      <div key={index} className="recent-called-number">{number}</div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="recent-called-numbers">
                  <div className="recent-called-numbers-grid">
                    {recentCalledNumbers.map((number, index) => (
                      <div key={index} className="recent-called-number">{number}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          <div className='boards-container'>

          {selectBoard && (
          <div className="bingo-header">
            <div className='selected-number'>
              <p className='selected-number-label'>የካርቴላ ቁጥር :-</p>
              <p className='selected-number-value'>{selectedNumber}</p>
            </div>
            <div className="bingo-letters">
              <span className='bingo-letter-text'>B</span>
              <span className='bingo-letter-text'>I</span>
              <span className='bingo-letter-text'>N</span>
              <span className='bingo-letter-text'>G</span>
              <span className='bingo-letter-text'>O</span>
            </div>
          </div>
          )

}

    
      <div className="bingo-board">
                  { selectBoard[0] && !isBingo && selectBoard[0].map((_, colIndex) => (
                    <div key={colIndex} className="board-row">
                      {selectBoard.map((row, rowIndex) => (
                        <div key={rowIndex}
                          className={`board-cell`}

                          // if cell is * it should always be green
                          style={{ backgroundColor: row[colIndex] === '*' ? '#4CAF50' : selectedCell.has(row[colIndex]) ? '#4CAF50' : '#2c2856',zIndex:1000 }}
                          id={`${row[colIndex] <= 15 && row[colIndex] > 0 ? 'b' : row[colIndex] <= 30 && row[colIndex] > 15 ? 'i' : row[colIndex] <= 45 && row[colIndex] > 30 ? 'n' : row[colIndex] <= 60 && row[colIndex] > 45 ? 'g' : row[colIndex] <= 75 && row[colIndex] > 60 ? 'o' : ''}${row[colIndex]}`}
                          onClick={() => {
                            handleCellClick(row[colIndex]);

                          }}
                        >
                          {row[colIndex]}
                        </div>
                      ))}
                    </div>
                  ))}

          

                </div>
            
        <button className={`bingo-button-card-${selectedNumber}`} 
              onClick={() => handleBingo(selectBoard,selectedNumber)} 
              disabled={firstBoardLost}
              style={{
                backgroundColor: firstBoardLost ? "red" : "orange"
              }}
          
          >
             {firstBoardLost ? "You made Faul" : "BINGO!"}
          </button>

          <div className='line'>

          </div>

         
        
          {selectedNumber2 !== null && (
          <div className="bingo-header">
            <div className='selected-number'>
              <p className='selected-number-label'>የካርቴላ ቁጥር :-</p>
              <p className='selected-number-value'>{selectedNumber2}</p>
            </div>
            <div className="bingo-letters">
              <span className='bingo-letter-text'>B</span>
              <span className='bingo-letter-text'>I</span>
              <span className='bingo-letter-text'>N</span>
              <span className='bingo-letter-text'>G</span>
              <span className='bingo-letter-text'>O</span>
            </div>
          </div>
          )

}

          <div className="bingo-board">
            {selectBoard2[0] && !isBingo && selectBoard2[0].map((_, colIndex) => (
              <div key={colIndex} className="board-row">
                {selectBoard2.map((row, rowIndex) => (
                  <div key={rowIndex}
                    className={`board-cell`}

                    // if cell is * it should always be green
                    style={{ backgroundColor: row[colIndex] === '*' ? '#4CAF50' : selectedCell.has(row[colIndex]) ? '#4CAF50' : '#2c2856' }}
                    id={`${row[colIndex] <= 15 && row[colIndex] > 0 ? 'b' : row[colIndex] <= 30 && row[colIndex] > 15 ? 'i' : row[colIndex] <= 45 && row[colIndex] > 30 ? 'n' : row[colIndex] <= 60 && row[colIndex] > 45 ? 'g' : row[colIndex] <= 75 && row[colIndex] > 60 ? 'o' : ''}${row[colIndex]}`}
                    onClick={() => {
                      handleCellClick(row[colIndex]);
                    }}
                  >
                    {row[colIndex]}
                  </div>
                ))}
              </div>
            ))}

          

          </div>


          </div>

        
       

       {selectedNumber2 !== null && (
          <div className="game-controls">
            <button className={`bingo-button-card-${selectedNumber2}`} 
                  onClick={() => handleBingo(selectBoard2,selectedNumber2)} 
                  disabled={secondBoardLost}
                  style={{
                    backgroundColor: secondBoardLost ? "red" : "orange"
                  }}
            >
             {secondBoardLost ? "You made Faul" : "BINGO!"}
            </button>
          </div>
       )}

        </div>
      </div>
</div>
      

    </div>
  );
};

export default PlayingBoard;
