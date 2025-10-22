import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import { BingoContext } from '../contexts/bingoContext';
import './gamePreview.css';

const GamePreview = () => {
  const {
    playerId,
    setPlayerId,
    roomId,
    setRoomId,
    playerName,
    setPlayerName,
    setToast,
    setIsToast
  } = useContext(BingoContext);

  const [gameState, setGameState] = useState(null);
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [lastBall, setLastBall] = useState(null);
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [winAmount, setWinAmount] = useState(0);
  const [isJoining, setIsJoining] = useState(false);
  const [recentCalledNumbers, setRecentCalledNumbers] = useState(['*', '*', '*']);

  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // Read URL parameters on component mount
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const urlPlayerId = queryParams.get('playerId');
    const urlRoomId = queryParams.get('betAmount');
    const urlPlayerName = queryParams.get('playerName');
    
    if (urlPlayerId) setPlayerId(urlPlayerId);
    if (urlRoomId) setRoomId(parseInt(urlRoomId));
    if (urlPlayerName && urlPlayerName !== 'null') setPlayerName(urlPlayerName);
    
    console.log('🎮 Game Preview - URL params:', { urlPlayerId, urlRoomId, urlPlayerName });
  }, []);

  // Socket event handlers
  useEffect(() => {
    if (!socket) return;

    const handleGameState = (data) => {
      console.log('🎮 Game Preview - Game state received:', data);
      setGameState(data);
      
      if (data.called_numbers && Array.isArray(data.called_numbers)) {
        const calledNumbersArray = data.called_numbers.map(ball => ball.number);
        setCalledNumbers(calledNumbersArray);
      }
      
      setLastBall(data.lastBall);
      setTotalPlayers(data.total_players || 0);
      setTotalCalledNumbers(data.total_called_numbers || 0);
      setWinAmount(data.win_amount || 0);
    };

    const handleJoinError = (data) => {
      console.log('❌ Join error:', data);
      setToast(data.message || 'Failed to join game');
      setIsToast(true);
      setIsJoining(false);
    };

    const handleJoinSuccess = () => {
      console.log('✅ Successfully joined game');
      setIsJoining(false);
      // Navigate to main game screen
      navigate(`/play?playerId=${encodeURIComponent(playerId)}&betAmount=${encodeURIComponent(roomId)}&playerName=${encodeURIComponent(playerName)}`);
    };

    socket.on('gameState', handleGameState);
    socket.on('joinError', handleJoinError);
    socket.on('joinSuccess', handleJoinSuccess);

    // Request current game state
    if (roomId) {
      socket.emit('handleRefresh', { gameId: roomId, roomId: roomId, playerId: playerId });
    }

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('joinError', handleJoinError);
      socket.off('joinSuccess', handleJoinSuccess);
    };
  }, [socket, roomId, playerId, playerName, navigate, setToast, setIsToast]);

  // Track recent balls
  useEffect(() => {
    if (!lastBall) return;
    const recentBall = `${lastBall.letter}${lastBall.number}`;
    setRecentCalledNumbers((prev) => {
      const updated = [...prev, recentBall];
      return updated.length > 3 ? updated.slice(1) : updated;
    });
  }, [lastBall]);

  const handleJoinGame = () => {
    if (!playerId || !roomId || !playerName) {
      setToast('Missing player information. Please refresh the page.');
      setIsToast(true);
      return;
    }

    setIsJoining(true);
    setToast('Joining game...');
    setIsToast(true);

    // Generate a random card number for the user
    const randomCardNumber = Math.floor(Math.random() * 1000) + 1;
    
    // Generate a simple board for preview (this will be replaced by actual board generation)
    const generateSimpleBoard = () => {
      const board = [];
      for (let i = 0; i < 5; i++) {
        const column = [];
        for (let j = 0; j < 5; j++) {
          if (i === 2 && j === 2) {
            column.push('*');
          } else {
            column.push(Math.floor(Math.random() * 15) + (i * 15) + 1);
          }
        }
        board.push(column);
      }
      return board;
    };

    const board = generateSimpleBoard();

    // Emit join game event
    socket.emit('joinGame', {
      playerId: playerId,
      roomId: roomId,
      selectedNumber: randomCardNumber,
      selectedNumber2: randomCardNumber + 1,
      selectBoard: board,
      selectBoard2: board,
      numberOfBoards: 1,
      playerName: playerName
    });
  };

  const handleGoBack = () => {
    navigate(`/?playerId=${encodeURIComponent(playerId)}&betAmount=${encodeURIComponent(roomId)}&playerName=${encodeURIComponent(playerName)}`);
  };

  return (
    <div className="game-container">
      {/* Header with back button */}
    
      {/* Stats bar - same as main screen */}
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
          <span>መደብ</span>
          <span>{roomId}</span>
        </div>
        <div className="stat-item">
          <span>ጥሪ</span>
          <span>{totalCalledNumbers}</span>
        </div>
      </div>

      <div className='middle-container'>
        {/* Called numbers section - same as main screen */}
        <div className="called-numbers">
          <div className="called-numbers-grid" style={{ gap: "2px" }}>
            <div className="column">
              <div className="column-header called-number-col" style={{
                backgroundColor: "#00022E",
                color: "white"
              }}>B</div>
              {Array.from({ length: 15 }, (_, i) => {
                const isCalled = calledNumbers?.includes(i + 1);
                const className = `number ${isCalled ? 'called' : ''}`;
                return (
                  <div 
                    key={i} 
                    className={className} 
                    id={`B${i + 1}`}
                  >
                    {i + 1}
                  </div>
                );
              })}
            </div>
            <div className="column">
              <div className="column-header called-number-col" style={{
                backgroundColor: "#00022E",
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
                backgroundColor: "#00022E",
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
                backgroundColor: "#00022E",
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
                backgroundColor: "#00022E",
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

        {/* Playing section - blurred */}
        <div className="bingo-content">
          <div className="playing-section">
            <div>
              <div className="current-call">
                {lastBall ? (
                  <div className="ball-display">
                    <div className='outer-circle'>
                      <div className='inner-circle'>
                        <div className="ball">
                          {lastBall.combined}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="waiting-state"></div>
                )}
              </div>

              {/* Recently Called Numbers */}
              <div className="recent-calls-container">
                <div className="recent-calls-numbers">
                  {recentCalledNumbers.map((number, index) => (
                    <div key={index} className={`recent-call-number ${number === '*' ? 'placeholder' : 'called'}`}>
                      {number}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Blurred playing area */}
            <div className='boards-container blurred-section'>
              <div className="blur-overlay">
                <div className="blur-content">
                  <div className="blur-message">
                    <h2>🎮 Game in Progress</h2>
                    <p>Join now to start playing!</p>
                    <button 
                      className={`join-game-button ${isJoining ? 'joining' : ''}`}
                      onClick={handleJoinGame}
                      disabled={isJoining}
                    >
                      {isJoining ? 'Joining...' : '🎮 Join This Game'}
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Blurred board preview */}
              <div className="board-row">
                <div className='board-cell-main header-bingo-style'>B</div>
                <div className='board-cell-main header-bingo-style'>I</div>
                <div className='board-cell-main header-bingo-style'>N</div>
                <div className='board-cell-main header-bingo-style'>G</div>
                <div className='board-cell-main header-bingo-style'>O</div>
              </div>
              
              {/* Sample blurred board */}
              <div className="bingo-board blurred">
                {Array.from({ length: 5 }, (_, rowIndex) => (
                  <div key={rowIndex} className="board-row">
                    {Array.from({ length: 5 }, (_, colIndex) => (
                      <div key={colIndex} className="board-cell-main blurred-cell">
                        {rowIndex === 2 && colIndex === 2 ? '*' : '?'}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GamePreview;
