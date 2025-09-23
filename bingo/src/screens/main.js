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
    setSelectedNumber,
    selectBoard,
    setSelectBoard,
    playersLength,
    countDown,
    setCountDown,
    roomId,
    setRoomId,
    playerId,
    setPlayerId,
    gameId,
    setGameId,
    setToast,
    setIsToast,
    playerName,
    setPlayerName,
    betAmount,
  } = useContext(BingoContext);

  const [calledNumbers, setCalledNumbers] = useState([]);
  const [lastBall, setLastBall] = useState(null);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [selectedCell, setSelectedCell] = useState(new Set());
  const [isBingo, setIsBingo] = useState(false);
  const [winningCard, setWinningCard] = useState(null);
  const [winner, setWinner] = useState(null);
  const [winnerCardNumber, setWinnerCardNumber] = useState(null);
  const [winnerPlayerName, setWinnerPlayerName] = useState(null);
  const [markedCells, setMarkedCells] = useState([]);
  const [firstBoardLost, setFirstBoardLost] = useState(false);
  const [winAmount, setWinAmount] = useState(0);
  const [totalWinAmount, setTotalWinAmount] = useState(0);
  const [totalPlayers,setTotalPlayers] = useState(0);
  const [recentCalledNumbers, setRecentCalledNumbers] = useState(['*', '*', '*']);

  // Generate Bingo board function
  const generateCombination = () => {
    const numbers = [];
    for (let i = 0; i < 5; i++) {
      const column = [];
      for (let j = 0; j < 5; j++) {
        if (i === 2 && j === 2) {
          column.push('FREE');
        } else {
          let num;
          do {
            num = Math.floor(Math.random() * 15) + (i * 15) + 1;
          } while (column.includes(num));
          column.push(num);
        }
      }
      numbers.push(column);
    }
    return numbers;
  };

  // Read URL parameters on component mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const urlPlayerId = queryParams.get('playerId');
    const urlRoomId = queryParams.get('betAmount');
    const urlPlayerName = queryParams.get('playerName');
    const urlSelectedNumber = queryParams.get('selectedNumber');
    
    if (urlPlayerId) setPlayerId(urlPlayerId);
    if (urlRoomId) setRoomId(parseInt(urlRoomId));
    if (urlPlayerName && urlPlayerName !== 'null') setPlayerName(urlPlayerName);
    if (urlSelectedNumber) {
      const selectedNum = parseInt(urlSelectedNumber);
      setSelectedNumber(selectedNum);
      // Generate selectBoard for the selected number
      setSelectBoard(generateCombination());
    }
    
    console.log('PlayingBoard - URL params:', { urlPlayerId, urlRoomId, urlPlayerName, urlSelectedNumber });
  }, []);

  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // ✅ Socket event bindings
  useEffect(() => {
    if (!socket) return;

    const handleGameState = (data) => {
      const calledNumber = data?.lastBall?.combined.split("-")[1]
      if(data.win_amount) {
        setWinAmount(data.win_amount)
        setTotalPlayers(data.total_players)
      }
      if(calledNumber){
        calledNumbers.push(parseInt(calledNumber))
        setCalledNumbers(calledNumbers)
      }
      setLastBall(data.lastBall);
      handlePlaySound(calledNumber)
      

      
      if (data.total_called_numbers) setTotalCalledNumbers(data.total_called_numbers);
      if (data.count_down) setCountDown(data.count_down);
      setGameId(data.gameId);
    };

  const handleFalseBingo = (data) => {
    const loserBoard = data.losser_board;
    if (loserBoard === selectedNumber) setFirstBoardLost(true);
  };

  const handleBingoWinner = (data) => {
    console.log('Bingo winner received:', data);
    if (data.isBingo) {
      setIsBingo(true);
      setWinningCard(data.winningCard);
      setWinner(data.winner);
      setWinnerCardNumber(data.winnerCardNumber);
      setWinnerPlayerName(data.winnerPlayerName);
      setMarkedCells(data.markedCells);
      toast.success(`${data.winnerPlayerName} won with Bingo!`);
    }
  };

    const handleGameOver = (data) => {
      if (data.roomId === roomId) {
        navigate(`/?playerId=${playerId}&&betAmount=${roomId}&playerName=${playerName}`);
      }
    };

    const handlePlaySound = async (calledNumber) => {
      const SOUND_URL = process.env.REACT_APP_SOUND_URL
      
      // Cache audio files to improve performance and reduce loading time
      if (!window.audioCache) {
        window.audioCache = new Map();
      }
      
      // Check if audio is already cached
      if (window.audioCache.has(calledNumber)) {
        const cachedAudio = window.audioCache.get(calledNumber);
        // Clone the audio to allow multiple simultaneous plays
        const audio = cachedAudio.cloneNode();
        audio.play().catch(error => {
          console.log('Cached audio play failed:', error);
        });
        return;
      }

      const soundUrl = `${SOUND_URL}/${calledNumber}.mp3`
      const audio = new Audio(soundUrl);
      audio.play().catch(error => {
        console.log('Audio play failed:', error);
      });

      // Cache the audio file
      window.audioCache.set(calledNumber, audio);
    };

    const handlePlayWinSound = async () => {
      const SOUND_URL = process.env.REACT_APP_SOUND_URL
      const soundUrl = `${SOUND_URL}/win.mp3`
      console.log("win soundUrl",soundUrl)
      const audio = new Audio(soundUrl);
      audio.play().catch(error => {
        console.log('Audio play failed:', error);
      });
    };

    const handleWinBingo = (data) => {
      if (data.winningCard) {
        setWinningCard(data.markedCells);
        setIsBingo(data.isBingo);
        setWinner(data.playerId);
        setWinnerCardNumber(data.winner_Number);
        setWinnerPlayerName(data.playerName);
        // handlePlayWinSound();
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
    socket.on('bingoWinner', handleBingoWinner);
    socket.on('joinError', handleJoinError);
    socket.on('playerLeft', handlePlayerLeft);

  

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
  }, [socket, roomId, playerId, playerName, selectedNumber, setCountDown, setGameId, setToast, setIsToast, navigate, winAmount, betAmount]);

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
    console.log('Bingo button clicked!', {
      totalCalledNumbers,
      gameId,
      roomId,
      playerId,
      markedCells: Array.from(selectedCell),
      playerName,
      board,
      boardNumber
    });
    
    if (totalCalledNumbers === 0) {
      toast.error('Game is not started yet');
      return;
    }
    
    if (selectedCell.size === 0) {
      toast.error('Please select some numbers first!');
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
    
    toast('Checking Bingo...', { icon: '🔍' });
  };


  socket.on('disconnect', () => {
    console.log('Socket disconnected, sending user and game data');
    socket.emit('userDisconnect', {
      playerId,
      playerName,
      roomId,
      gameId,
      selectedNumber,
      markedCells: Array.from(selectedCell),
      reason: 'disconnect'
    });

  });
  

  const handleRefresh = () => {
    socket.emit('handleRefresh', { gameId, roomId, playerId });
  };

  const handleLeave = (reason) => {
    socket.emit('leave', { playerId, roomId, selectedNumber, reason });
  };

  const handleCellClick = (cell) => {
    setSelectedCell((prev) => {
      const updated = new Set(prev);
      if (updated.has(cell)) {
        updated.delete(cell);
        console.log('Removed cell:', cell, 'Selected cells:', Array.from(updated));
      } else {
        updated.add(cell);
        console.log('Added cell:', cell, 'Selected cells:', Array.from(updated));
      }
      return updated;
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
  {/* Header row */}
  <div className="winning-card-row">
    {["B", "I", "N", "G", "O"].map((letter, index) => (
      <div key={index} className="winning-card-cell">
        <span>{letter}</span>
      </div>
    ))}
  </div>

  {winningCard[0] && winningCard[0].map((_, rowIndex) => (
    <div key={rowIndex} className="winning-card-row">
      {winningCard.map((row, colIndex) => {
        const cell = row[rowIndex];
        // Check win conditions
        const rowComplete = winningCard.every(r => r[rowIndex].marked);
        const colComplete = winningCard[colIndex].every(c => c.marked);
        const diagonalComplete =
          rowIndex === colIndex && winningCard.every((r, i) => r[i].marked);
        const reverseDiagonalComplete =
          rowIndex + colIndex === 4 && winningCard.every((r, i) => r[4 - i].marked);

        const fourCornersComplete =
          winningCard[0][0].marked &&
          winningCard[0][4].marked &&
          winningCard[4][0].marked &&
          winningCard[4][4].marked;

        const fourEdgesComplete =
          winningCard[0][2].marked &&
          winningCard[2][0].marked &&
          winningCard[2][4].marked &&
          winningCard[4][2].marked;

        // Does this cell belong to a winning line?
        const inWinningLine =
          (rowComplete && cell.marked) ||
          (colComplete && cell.marked) ||
          (diagonalComplete && cell.marked) ||
          (reverseDiagonalComplete && cell.marked) ||
          (fourCornersComplete &&
            cell.marked &&
            ((colIndex === 0 && (rowIndex === 0 || rowIndex === 4)) ||
             (colIndex === 4 && (rowIndex === 0 || rowIndex === 4)))) ||
          (fourEdgesComplete &&
            cell.marked &&
            ((colIndex === 0 && rowIndex === 2) ||
             (colIndex === 2 && (rowIndex === 0 || rowIndex === 4)) ||
             (colIndex === 4 && rowIndex === 2)));

        // Final background color
        let bgColor = "white";
        if (inWinningLine) {
          bgColor = "green";   // part of winning line
        } else if (cell.marked) {
          bgColor = "red";     // marked but not winning
        }

        return (
          <div
            key={colIndex}
            className="winning-card-cell"
            style={{ backgroundColor: bgColor }}
          >
            <span>{cell.number}</span>
          </div>
        );
      })}
    </div>
  ))}
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
          <span>{isNaN(winAmount.toFixed(2)) ? 0 : (winAmount.toFixed(2))}</span>
        </div>
        <div className="stat-item">
          <span>ብዛት</span>
          
          <span>{totalPlayers}</span>
        </div>
        <div className="stat-item">
          <span>መደብ </span>
        
          <span>{roomId}</span>
        </div>
        <div className="stat-item">
          <span>ጥሪ </span>
          <span>{totalCalledNumbers}</span>
        </div>
      </div>

<div className='middle-container'>
<div className="called-numbers">
        
        <div className="called-numbers-grid" style={{
          gap:"2px"
        }}>
          
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "#d32f2f", /* Red for B */
              color: "white"
            }}>B</div>
            {Array.from({ length: 15 }, (_, i) => (
              <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'last-called' : ''} ${selectedNumber == i + 1 ? 'selected' : ''}`}
                id={`B${i + 1}`}

              >
                {i + 1}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "#FFD700", /* Yellow for I */
              color: "#000"
            }}>I</div>
            {Array.from({ length: 15 }, (_, i) => (
            <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'last-called' : ''} ${selectedNumber == i + 16 ? 'selected' : ''}`}
                id={`I${i + 16}`}
              >
                {i + 16}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "#4CAF50", /* Green for N */
              color: "white"
            }}>N</div>
            {Array.from({ length: 15 }, (_, i) => (
            <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'last-called' : ''} ${selectedNumber == i + 31 ? 'selected' : ''}`}
                id={`N${i + 31}`}

              >
                {i + 31}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "#2196F3", /* Blue for G */
              color: "white"
            }}>G</div>
            {Array.from({ length: 15 }, (_, i) => (
              <div key={i}
                className={`number ${calledNumbers?.includes(i + 46) ? 'last-called' : ''} ${selectedNumber == i + 46 ? 'selected' : ''}`}
                id={`G${i + 46}`}
              >
                {i + 46}
              </div>
            ))}
          </div>
          <div className="column">
            <div className="column-header called-number-col" style={{
              backgroundColor: "#9C27B0", /* Purple for O */
              color: "white"
            }}>O</div>
            {Array.from({ length: 15 }, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 61) ? 'last-called' : ''} ${selectedNumber == i + 61 ? 'selected' : ''}  `}
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

        

          <div className='boards-container'>

          {selectBoard && (
          <div className="board-row">
          
            <div className="bingo-letters-main">
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
                          className={`board-cell-main`}
                          // if cell is * it should always be golden, selected cells should be yellow
                          style={{ 
                            background: row[colIndex] === 'FREE' ? 'goldenrod' : selectedCell.has(row[colIndex]) ? 'orange' : '#ffffff',
                            border: selectedCell.has(row[colIndex]) ? '2px solid #ff6600' : '1px solid #34495e'
                          }}
                          id={`${row[colIndex] <= 15 && row[colIndex] > 0 ? 'b' : row[colIndex] <= 30 && row[colIndex] > 15 ? 'i' : row[colIndex] <= 45 && row[colIndex] > 30 ? 'n' : row[colIndex] <= 60 && row[colIndex] > 45 ? 'g' : row[colIndex] <= 75 && row[colIndex] > 60 ? 'o' : ''}${row[colIndex]}`}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleCellClick(row[colIndex]);
                          }}
                        >
                          {row[colIndex]}
                        </div>
                      ))}
                    </div>
                  ))}

                </div>

            <div className='selected-number'>
              <p className='selected-number-label'>የካርቴላ ቁጥር :-</p>
              <p className='selected-number-value'>{selectedNumber}</p>
            </div>
            
            <button className={`bingo-button-card-${selectedNumber}`} 
                  onClick={() => handleBingo(selectBoard,selectedNumber)} 
                  disabled={firstBoardLost || !selectedNumber}
                  style={{
                    backgroundColor: firstBoardLost ? "red" : "orange",
                    cursor: firstBoardLost || !selectedNumber ? "not-allowed" : "pointer"
                  }}
            >
               {firstBoardLost ? "You made Faul" : "BINGO!"}
            </button>

          </div>

        </div>
      </div>

    
</div>
      
    </div>
  );
};

export default PlayingBoard;
