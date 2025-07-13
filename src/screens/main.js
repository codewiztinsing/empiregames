import React, { useState, useContext, useEffect, use } from 'react';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import BingoWinner from '../components/BingoWinner';
const PlayingBoard = () => {
  const { selectedNumber, selectBoard, playersLength, countDown, roomId, playerId, gameId, setGameId, setToast, setIsToast } = useContext(BingoContext);

  const [board, setBoard] = useState(Array(5).fill().map(() => Array(5).fill(null)));
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [currentCall, setCurrentCall] = useState(null);
  const [lastBall, setLastBall] = useState(0);
  const [winAmount, setWinAmount] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [selectedCell, setSelectedCell] = useState(new Set());
  const [isBingo, setIsBingo] = useState(false);
  const [winningCard, setWinningCard] = useState([]);
  const [recentCalledNumbers, setRecentCalledNumbers] = useState([1,2,3,4,5]);
  const [winner, setWinner] = useState("skdfn9123u42139")
  // const [betAmount, setBetAmount] = useState(0);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();


  useEffect(() => {
    socket.on('numberSelected', (number) => {
      setCurrentCall(number);
    });

    if (lastBall) {
      const element = document.getElementById(`${lastBall.letter}${lastBall.number}`);
      if (element) {
        element.classList.add('called');
      }
    }



    return () => {
      socket.off('numberSelected');
    };
  }, [socket, lastBall, selectedCell, isBingo]);

  const handleBingo = () => {


    socket.emit('bingo', {
      gameId: gameId,
      roomId: roomId,
      playerId: playerId,
      markedCells: Array.from(selectedCell)
    });

  };

  function handleGameState(data) {
    console.log("data in gameState", data)
    if (data.lastBall && data.lastBall.length > 0 && data.roomId == roomId) {
      setLastBall(data.lastBall[data.lastBall.length - 1]);
    }


    setLastBall(data.lastBall)
    if (data.total_called_numbers) {
      setTotalCalledNumbers(data.total_called_numbers)
    }
    setGameId(data.gameId)
  }

  socket.on('gameState', handleGameState);


  const handleRefresh = () => {
    console.log("refresh for ", gameId, roomId, playerId)
    socket.emit('handleRefresh', {
      gameId: gameId,
      roomId: roomId,
      playerId: playerId
    });

  };




  socket.on('gameOver', (data) => {
    console.log("data in gameOver", data);
    if (data.roomId == roomId) {
      navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);
    }
  })

  socket.on('winBingo', (data) => {
    console.log("data in winBingo 2", data);
    if (data.winningCard) {
      setWinningCard(data.markedCells)
      setIsBingo(data.isBingo)
      setWinner(data.playerId)

    }
  })

  socket.on('falseBingo', (data) => {
    if (data.isBingo === false) {

      if (data.playerId === playerId) {
        navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);
        window.location.reload();
      }
    }
    if (data.playerId === playerId) {
      setToast("Invalid Bingo Call!");
      setIsToast(true);
      setTimeout(() => {
        setIsToast(false);
      }, 3000);
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
      selectedNumber

    })
    navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);

    window.location.reload();
  };

  const handleCellClick = (cell) => {
    console.log("cell", selectedCell.has(cell));
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

      {isBingo && (
        <div className="bingo-winner-overlay">
          <div className="bingo-winner-card">


            <h2>{playerId === winner ? "You Won!" : `Player ${winner} Won!`}</h2>
            <div className="winning-card">
              {winningCard.map((row, rowIndex) => (
                <div key={rowIndex} className="winning-card-row">
                  {row.map((cell, cellIndex) => (
                    <div
                      key={cellIndex}
                      className={`winning-card-cell ${cell.marked ? 'marked' : ''}`}
                    >
                      {cell.number}
                    </div>
                  ))}
                </div>
              ))}
            </div>
            <button
              className="close-winner-button"
              onClick={handleCloseWinner}
            >
              Close
            </button>
          </div>
        </div>
      )}

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
              {Array.from({ length: 15 }, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 1) ? 'called' : ''}`}
                  id={`B${i + 1}`}

                >
                  {i + 1}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">I</div>
              {Array.from({ length: 15 }, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 16) ? 'called' : ''}`}
                  id={`I${i + 16}`}

                >
                  {i + 16}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">N</div>
              {Array.from({ length: 15 }, (_, i) => (
                <div key={i} className={`number ${calledNumbers?.includes(i + 31) ? 'called' : ''}`}
                  id={`N${i + 31}`}

                >
                  {i + 31}
                </div>
              ))}
            </div>
            <div className="column">
              <div className="column-header">G</div>
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
              <div className="column-header">O</div>
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

                      <p style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center', color: 'white', width: '100%', height: '100%', fontWeight: 'bold' }}>Game starting</p>
                      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center', color: 'white', width: '100%', height: '100%', fontWeight: 'bold' }}>{countDown}</div>

                    </div>
                  ) : (
                    <p style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', textAlign: 'center', color: 'white', width: '100%', height: '100%', fontWeight: 'bold' }}>Game to start...</p>
                  )}
                </div>
              )}
            </div>
          </div>

    
          <div className="recent-called-numbers">
            <div className="recent-called-numbers-grid">
              {recentCalledNumbers.map((number, index) => (
                <div key={index} className="recent-called-number">{number}</div>
              ))}
            </div>
          </div>

        
          <div className="bingo-header">
            <div className="bingo-letters">
              <span style={{color: "white",width:"30px",height:"30px",backgroundColor:"orange",borderRadius:"50%",display:"flex",justifyContent:"center",alignItems:"center"}}>B</span>
              <span style={{color: "white",width:"30px",height:"30px",backgroundColor:"green",borderRadius:"50%",display:"flex",justifyContent:"center",alignItems:"center"}}>I</span>
              <span style={{color: "white",width:"30px",height:"30px",backgroundColor:"blue",borderRadius:"50%",display:"flex",justifyContent:"center",alignItems:"center"}}>N</span>
              <span style={{color: "white",width:"30px",height:"30px",backgroundColor:"red",borderRadius:"50%",display:"flex",justifyContent:"center",alignItems:"center"}}>G</span>
              <span style={{color: "white",width:"30px",height:"30px",backgroundColor:"purple",borderRadius:"50%",display:"flex",justifyContent:"center",alignItems:"center"}}>O</span>
            </div>
          </div>

          <div className="bingo-board">
            {selectBoard.map((row, rowIndex) => (
              <div key={rowIndex} className="board-row">
                {row.map((cell, colIndex) => (
                  <div key={colIndex}
                    className={`board-cell`}
                    style={{ backgroundColor: selectedCell.has(cell) ? '#4CAF50' : 'white' }}
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

            <div className='selected-number'>
              <p className='selected-number-label'>Board Number</p>
              <p className='selected-number-value'>{selectedNumber}</p>
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
  );
};

export default PlayingBoard;
