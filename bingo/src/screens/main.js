import React, { useState, useContext, useEffect, use } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import BingoWinner from '../components/BingoWinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';




const PlayingBoard = () => {
  const { selectedNumber,selectedNumber2, selectBoard,selectBoard2, playersLength, countDown,setCountDown, roomId, playerId, gameId, setGameId, setToast, setIsToast, playerName } = useContext(BingoContext);

  const [board, setBoard] = useState(Array(5).fill().map(() => Array(5).fill(null)));
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [currentCall, setCurrentCall] = useState(null);
  const [lastBall, setLastBall] = useState(0);
  const [winAmount, setWinAmount] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [selectedCell, setSelectedCell] = useState(new Set());
  const [isBingo, setIsBingo] = useState(false);
  const [winningCard, setWinningCard] = useState([]);
  const [recentCalledNumbers, setRecentCalledNumbers] = useState(["*","*","*"]);
  const [winner, setWinner] = useState("skdfn9123u42139")
  const [winnerCardNumber, setWinnerCardNumber] = useState(0);  
  const [hasToasted, setHasToasted] = useState(false);
  const [winnerPlayerName, setWinnerPlayerName] = useState("");
  // const [betAmount, setBetAmount] = useState(0);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();


  useEffect(() => {
   
    socket.on('numberSelected', (number) => {
      setCurrentCall(number);
    });

    if (lastBall) {
      const element = document.getElementById(`${lastBall.letter}${lastBall.number}`);
      const recentBall = `${lastBall.letter}${lastBall.number}`
      setRecentCalledNumbers(prev => [...prev,recentBall])
      if (recentCalledNumbers.length > 3) {
        setRecentCalledNumbers(prev => prev.slice(1));
      }
      element.classList.add("last-called")
    
      
    }



    return () => {
      socket.off('numberSelected');
    };
  }, [socket, lastBall, selectedCell, isBingo]);

  const handleBingo = () => {
    if(totalCalledNumbers === 0){
      toast.error("Game is not started yet");
      return;
    }
   
    console.log("player name = ",playerName)

    socket.emit('bingo', {
      gameId: gameId,
      roomId: roomId,
      playerId: playerId,
      markedCells: Array.from(selectedCell),
      selectedNumber: selectedNumber,
      selectedNumber2: selectedNumber2,
      playerName: playerName
    });

  };

  function handleGameState(data) {
    console.log(data);
 

    if (data.lastBall && data.lastBall.length > 0 && data.roomId == roomId) {
      setLastBall(data.lastBall[data.lastBall.length - 1]);   
      setRecentCalledNumbers(prev => [...prev, data.lastBall[data.lastBall.length - 1]]);
      if (recentCalledNumbers.length > 3) {
        setRecentCalledNumbers(prev => prev.slice(1));
      }
    }


    setLastBall(data.lastBall)
   
    if (data.total_called_numbers) {
      setTotalCalledNumbers(data.total_called_numbers)
    }
    if (data.count_down) {
      setCountDown(data.count_down)
    }

    
    setGameId(data.gameId)
  }

  socket.on('gameState', handleGameState);


  const handleRefresh = () => {
    socket.emit('handleRefresh', {
      gameId: gameId,
      roomId: roomId,
      playerId: playerId
    });

  };




  socket.on('gameOver', (data) => {
    if (data.roomId == roomId) {
      navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);
    }
  })

  socket.on('winBingo', (data) => {
    if (data.winningCard) {

     
        setWinningCard(data.markedCells)
        setIsBingo(data.isBingo)
        setWinner(data.playerId)
        setWinnerCardNumber(data.winner_Number)
        setWinnerPlayerName(data.playerName)
      
     
    }
  })

  socket.on('falseBingo', (data) => {
    if (data.isBingo === false) {
      if (data.playerId === playerId) {
        console.log("false bingo");
        if (hasToasted) return;
        setHasToasted(true);
        toast.error("Invalid Bingo claim!");
        return 
        setTimeout(() => {
          navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);
          window.location.reload();
        }, 3000);
          
        }
    }
   

  })

  socket.on('joinError', (data) => {
    if (data.roomId == roomId) {
      setToast(data.message);
      setIsToast(true);
      navigate(`/selection?playerId=${playerId}&betAmount=${roomId}`);
    }

  })


  const handleLeave = () => {
    socket.emit("leave", {
      playerId,
      roomId,
      selectedNumber,
      selectedNumber2

    })
    navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);

    window.location.reload();
  };




  const handleCellClick = (cell) => {
    const updatedSet = new Set(selectedCell);

    if (updatedSet.has(cell)) {
      updatedSet.delete(cell);
    } else {
      updatedSet.add(cell);
    }

    setSelectedCell(updatedSet);
  };


  const handleCloseWinner = () => {

    setIsBingo(false);
    const queryParams =
      navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);
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

      <p className='winner-card-header-winner-number'>አሸናፊ ካርድ ቁጥር : {winnerCardNumber}</p>
      <p className='winner-card-header-text'>ስም : {winnerPlayerName},is Winner</p>


      <div className="winning-card">
        <div className="winning-card-row">
          {["B", "I", "N", "G", "O"].map((letter, index) => (
            <div key={index} className="winning-card-cell">
              <span>{letter}</span>
            </div>
          ))}
        </div>

        {winningCard.map((row, rowIndex) => {
          const isRowComplete = row.every(cell => cell.marked);
          const isColumnComplete = winningCard.every(r => r[rowIndex].marked);
          const isDiagonalComplete = winningCard.every(r => r[rowIndex].marked);
          const isReverseDiagonalComplete = winningCard.every(r => r[rowIndex].marked);
          const isFourCornersComplete = winningCard.every(r => r[rowIndex].marked);
          const isFourEdgesComplete = winningCard.every(r => r[rowIndex].marked);
          

          return (
            <div key={rowIndex} className="winning-card-row">
              {row.map((cell, cellIndex) => (
                <div
                  key={cellIndex}
                  className="winning-card-cell"
                  style={{
                    backgroundColor: isRowComplete || isColumnComplete || isDiagonalComplete || isReverseDiagonalComplete || isFourCornersComplete || isFourEdgesComplete
                      ? '#ff0000'
                      : cell.marked
                      ? '#00ff00'
                      : 'transparent',
                  }}
                >
                  <span>{cell.number}</span>
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
              <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'called' : ''}`}
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
              <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'called' : ''}`}
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
              <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'called' : ''}`}
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
                className={`number ${calledNumbers?.includes(i + 46) ? 'called' : ''}`}
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
              <div key={i} className={`number ${calledNumbers?.includes(i + 61) ? 'called' : ''}`}
                id={`O${i + 61}`}

              >
                {i + 61}
              </div>
            ))}
          </div>
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
                  { !isBingo && selectBoard.map((row, rowIndex) => (
                    <div key={rowIndex} className="board-row">
                      {row.map((cell, colIndex) => (
                        <div key={colIndex}
                          className={`board-cell`}

                          // if cell is * it should always be green
                          style={{ backgroundColor: cell === '*' ? '#4CAF50' : selectedCell.has(cell) ? '#4CAF50' : '#2c2856',zIndex:1000 }}
                          id={`${cell <= 15 && cell > 0 ? 'b' : cell <= 30 && cell > 15 ? 'i' : cell <= 45 && cell > 30 ? 'n' : cell <= 60 && cell > 45 ? 'g' : cell <= 75 && cell > 60 ? 'o' : ''}${cell}`}
                          onClick={() => {
                            handleCellClick(cell);

                          }}
                        >
                          {cell}
                        </div>
                      ))}
                    </div>
                  ))}

          

                </div>
            

          <div className='line'>

          </div>

         
        
          {selectBoard2 !== null && (
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
            {selectBoard2.map((row, rowIndex) => (
              <div key={rowIndex} className="board-row">
                {row.map((cell, colIndex) => (
                  <div key={colIndex}
                    className={`board-cell`}

                    // if cell is * it should always be green
                    style={{ backgroundColor: cell === '*' ? '#4CAF50' : selectedCell.has(cell) ? '#4CAF50' : '#2c2856' }}
                    id={`${cell <= 15 && cell > 0 ? 'b' : cell <= 30 && cell > 15 ? 'i' : cell <= 45 && cell > 30 ? 'n' : cell <= 60 && cell > 45 ? 'g' : cell <= 75 && cell > 60 ? 'o' : ''}${cell}`}
                    onClick={() => {
                      handleCellClick(cell);
                    }}
                  >
                    {cell}
                  </div>
                ))}
              </div>
            ))}

          

          </div>


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
      

    </div>
  );
};

export default PlayingBoard;
