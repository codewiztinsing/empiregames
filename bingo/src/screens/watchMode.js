import React, { useState, useContext, useEffect, useCallback, useMemo } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './watchMode.css';
import { BingoContext } from '../contexts/bingoContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog, faVolumeMute, faVolumeUp, faSignOutAlt, faSync, faEye } from '@fortawesome/free-solid-svg-icons';
import { useTranslation } from 'react-i18next';
import LanguageSelector from '../components/LanguageSelector';

const WatchModeScreen = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const socket = useContext(SocketContext);
  
  // Get URL parameters
  const playerId = searchParams.get('playerId');
  const betAmount = searchParams.get('betAmount');
  const playerName = searchParams.get('playerName');
  
  const {
    selectedNumber,
    setSelectedNumber,
    selectBoard,
    setSelectBoard,
    playersLength,
    setPlayersLength,
    countDown,
    setCountDown,
    roomId,
    setRoomId,
    setPlayerId,
    gameId,
    setGameId,
    setToast,
    setIsToast,
    setPlayerName,
    betAmount: contextBetAmount,
  } = useContext(BingoContext);

  // Game state for watch mode
  const [gameState, setGameState] = useState({
    calledNumbers: [],
    lastBall: null,
    totalCalledNumbers: 0,
    isBingo: false,
    winner: null,
    winnerCardNumber: null,
    winnerPlayerName: null,
    winningCard: null,
    totalPlayers: 0,
    winAmount: 0,
    recentCalledNumbers: ['*', '*', '*'],
    winnerCountdown: 5,
    isMuted: false,
    gameCountdown: 0,
    gameStatus: 'waiting',
    showDepositReminder: false,
    depositReminderDismissed: false,
    // Watch mode specific
    activePlayers: [],
    gameProgress: 0,
    currentRound: 1,
  });

  // Watch mode specific state
  const [isWatching, setIsWatching] = useState(true);
  const [showPlayerCards, setShowPlayerCards] = useState(false);

  // Destructure for easier access
  const {
    calledNumbers,
    lastBall,
    totalCalledNumbers,
    isBingo,
    winner,
    winnerCardNumber,
    winnerPlayerName,
    winningCard,
    totalPlayers,
    winAmount,
    recentCalledNumbers,
    winnerCountdown,
    isMuted,
    gameCountdown,
    gameStatus,
    activePlayers,
    gameProgress,
    currentRound,
  } = gameState;

  // Initialize watch mode
  useEffect(() => {
    if (playerId) {
      setPlayerId(playerId);
    }
    if (betAmount) {
      setRoomId(betAmount);
    }
    if (playerName) {
      setPlayerName(playerName);
    }
    
    console.log("🎮 Watch Mode initialized:", { playerId, betAmount, playerName });
    toast.success("🎮 Welcome to Watch Mode! Observing the current game...");
    
    // Set some default/fallback data for testing
    setGameState(prev => ({
      ...prev,
      totalPlayers: prev.totalPlayers || 5, // Fallback
      totalCalledNumbers: prev.totalCalledNumbers || 15, // Fallback
      recentCalledNumbers: prev.recentCalledNumbers || ['B12', 'I23', 'N34'], // Fallback
      calledNumbers: prev.calledNumbers || ['B1', 'B2', 'B3', 'I16', 'I17', 'I18', 'N31', 'N32', 'N33', 'G46', 'G47', 'G48', 'O61', 'O62', 'O63'], // Fallback
      gameStatus: prev.gameStatus || 'in-progress', // Fallback
      currentRound: prev.currentRound || 1, // Fallback
    }));
  }, [playerId, betAmount, playerName, setPlayerId, setRoomId, setPlayerName]);

  // Socket event handlers
  const handleGameState = useCallback((data) => {
    console.log('Watch Mode - Game state update:', data);
    setGameState(prev => ({
      ...prev,
      calledNumbers: data.calledNumbers || data.called_numbers || prev.calledNumbers,
      lastBall: data.lastBall || data.last_ball || prev.lastBall,
      totalCalledNumbers: data.totalCalledNumbers || data.total_called_numbers || prev.totalCalledNumbers,
      totalPlayers: data.totalPlayers || data.total_players || prev.totalPlayers,
      winAmount: data.winAmount || data.win_amount || prev.winAmount,
      gameStatus: data.gameStatus || data.game_status || prev.gameStatus,
      recentCalledNumbers: data.recentCalledNumbers || data.recent_called_numbers || prev.recentCalledNumbers,
      activePlayers: data.activePlayers || data.active_players || prev.activePlayers,
      gameProgress: data.gameProgress || data.game_progress || prev.gameProgress,
      currentRound: data.currentRound || data.current_round || prev.currentRound,
    }));
  }, []);

  const handleBingoWinner = useCallback((data) => {
    console.log('Watch Mode - Bingo winner:', data);
    setGameState(prev => ({
      ...prev,
      isBingo: true,
      winner: data.winnerPlayerName || data.winner_player_name,
      winnerCardNumber: data.winnerCardNumber || data.winner_card_number,
      winnerPlayerName: data.winnerPlayerName || data.winner_player_name,
      winningCard: data.winningCard || data.winning_card,
    }));
  }, []);

  const handleNextBall = useCallback((data) => {
    console.log('Watch Mode - Next ball:', data);
    setGameState(prev => ({
      ...prev,
      calledNumbers: data.calledNumbers || data.called_numbers || prev.calledNumbers,
      lastBall: data.lastBall || data.last_ball || prev.lastBall,
      totalCalledNumbers: data.totalCalledNumbers || data.total_called_numbers || prev.totalCalledNumbers,
      recentCalledNumbers: data.recentCalledNumbers || data.recent_called_numbers || prev.recentCalledNumbers,
    }));
  }, []);

  const handlePlayerUpdate = useCallback((data) => {
    console.log('Watch Mode - Player update:', data);
    setGameState(prev => ({
      ...prev,
      totalPlayers: data.totalPlayers || data.total_players || prev.totalPlayers,
      winAmount: data.winAmount || data.win_amount || prev.winAmount,
      activePlayers: data.activePlayers || data.active_players || prev.activePlayers,
    }));
  }, []);

  // Socket event listeners
  useEffect(() => {
    if (socket) {
      socket.on('gameState', handleGameState);
      socket.on('bingoWinner', handleBingoWinner);
      socket.on('nextBall', handleNextBall);
      socket.on('playerUpdate', handlePlayerUpdate);
      socket.on('gameStatus', handleGameState);
      socket.on('ballDisplay', handleNextBall);
      socket.on('playerJoined', handlePlayerUpdate);
      socket.on('playerLeft', handlePlayerUpdate);

      return () => {
        socket.off('gameState', handleGameState);
        socket.off('bingoWinner', handleBingoWinner);
        socket.off('nextBall', handleNextBall);
        socket.off('playerUpdate', handlePlayerUpdate);
        socket.off('gameStatus', handleGameState);
        socket.off('ballDisplay', handleNextBall);
        socket.off('playerJoined', handlePlayerUpdate);
        socket.off('playerLeft', handlePlayerUpdate);
      };
    }
  }, [socket, handleGameState, handleBingoWinner, handleNextBall, handlePlayerUpdate]);

  // Handle winner countdown
  useEffect(() => {
    if (isBingo && winnerCountdown > 0) {
      const timer = setTimeout(() => {
        setGameState(prev => ({
          ...prev,
          winnerCountdown: prev.winnerCountdown - 1,
        }));
      }, 1000);

      return () => clearTimeout(timer);
    } else if (isBingo && winnerCountdown === 0) {
      // Navigate back to selection screen after winner countdown
      setTimeout(() => {
        navigate('/');
      }, 2000);
    }
  }, [isBingo, winnerCountdown, navigate]);

  // Toggle mute
  const toggleMute = () => {
    setGameState(prev => ({
      ...prev,
      isMuted: !prev.isMuted,
    }));
  };

  // Toggle player cards visibility
  const togglePlayerCards = () => {
    setShowPlayerCards(!showPlayerCards);
  };

  // Leave watch mode
  const leaveWatchMode = () => {
    navigate('/');
  };

  // Manual refresh for testing
  const refreshData = () => {
    console.log('🔄 Manual refresh triggered');
    setGameState(prev => ({
      ...prev,
      totalPlayers: prev.totalPlayers + 1, // Test increment
      totalCalledNumbers: prev.totalCalledNumbers + 1, // Test increment
      lastBall: `B${Math.floor(Math.random() * 15) + 1}`, // Random test ball
    }));
    toast.success('🔄 Data refreshed!');
  };

  // Render player card (blurred for privacy)
  const renderPlayerCard = (player, index) => (
    <div key={index} className="player-card-watch">
      <div className="player-card-header">
        <div className="player-name">{player.name || `Player ${index + 1}`}</div>
        <div className="player-status">🎮 Playing</div>
      </div>
      <div className="player-card-grid">
        {Array.from({ length: 25 }, (_, cellIndex) => (
          <div key={cellIndex} className="player-card-cell">
            <div className="player-card-number">
              {cellIndex === 12 ? '★' : '?'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="watch-mode-container">
      <Toaster />
      
      {/* Debug Information */}
      <div className="debug-info" style={{ 
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        background: 'rgba(0,0,0,0.8)', 
        color: 'white', 
        padding: '10px', 
        borderRadius: '5px',
        fontSize: '12px',
        zIndex: 1000
      }}>
        <div>Total Players: {totalPlayers}</div>
        <div>Called Numbers: {totalCalledNumbers}</div>
        <div>Game Status: {gameStatus}</div>
        <div>Called Numbers Array: {calledNumbers.length}</div>
        <div>Recent Numbers: {recentCalledNumbers.length}</div>
        <div>Last Ball: {lastBall ? (typeof lastBall === 'object' ? lastBall.number || lastBall.combined : lastBall) : 'None'}</div>
      </div>

      {/* Header */}
      <div className="watch-mode-header">
        <div className="watch-mode-title">
          <FontAwesomeIcon icon={faEye} className="watch-icon" />
          <span>Watch Mode</span>
        </div>
        <div className="watch-mode-controls">
          <button 
            className={`control-btn ${showPlayerCards ? 'active' : ''}`}
            onClick={togglePlayerCards}
            title="Toggle Player Cards"
          >
            <FontAwesomeIcon icon={faEye} />
          </button>
          <button 
            className={`control-btn ${isMuted ? 'active' : ''}`}
            onClick={toggleMute}
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            <FontAwesomeIcon icon={isMuted ? faVolumeMute : faVolumeUp} />
          </button>
          <button 
            className="control-btn"
            onClick={refreshData}
            title="Refresh Data"
          >
            <FontAwesomeIcon icon={faSync} />
          </button>
          <button 
            className="control-btn"
            onClick={leaveWatchMode}
            title="Leave Watch Mode"
          >
            <FontAwesomeIcon icon={faSignOutAlt} />
          </button>
        </div>
      </div>

      {/* Top Stats Bar */}
      <div className="top-stats-bar">
        <div className="stat-item purple">Bet {betAmount} ETB</div>
        <div className="stat-item blue">Players {totalPlayers}</div>
        <div className="stat-item green">Prize {winAmount} ETB</div>
        <div className="stat-item light-green">Called {totalCalledNumbers}/75</div>
        
      
      </div>

      {/* Main Game Area */}
      <div className="main-game-area">
        {/* Left Side - Called Numbers Board */}
        <div className="called-numbers-section">
          <div className="section-title">Called Numbers Board</div>
          <div className="bingo-numbers-board">
            {Array.from({ length: 75 }, (_, index) => {
              const number = index + 1;
              const isCalled = calledNumbers.some(calledNum => {
                const calledNumber = typeof calledNum === 'object' ? calledNum.number || calledNum.combined : calledNum;
                return calledNumber === number || calledNumber === `B${number}` || calledNumber === `I${number}` || calledNumber === `N${number}` || calledNumber === `G${number}` || calledNumber === `O${number}`;
              });
              
              return (
                <div 
                  key={number} 
                  className={`bingo-number-cell ${isCalled ? 'called' : ''}`}
                >
                  {number}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side - Game Info */}
        <div className="game-info-section">
          {/* Current Ball */}
          {lastBall && (
            <div className="current-ball-section">
              <div className="current-ball-label">Current Ball</div>
              <div className="current-ball">
                <div className="ball-number">
                  {typeof lastBall === 'object' ? lastBall.number || lastBall.combined : lastBall}
                </div>
              </div>
            </div>
          )}

          {/* Recent Called Numbers */}
          <div className="recent-numbers-section">
            <div className="section-title">Recent Numbers</div>
            <div className="recent-numbers">
              {recentCalledNumbers.map((number, index) => (
                <div key={index} className="recent-number">
                  {typeof number === 'object' ? number.number || number.combined : number}
                </div>
              ))}
            </div>
          </div>

          {/* Game Progress */}
          <div className="game-progress-section">
            <div className="section-title">Game Progress</div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(totalCalledNumbers / 75) * 100}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {totalCalledNumbers} / 75 numbers called
            </div>
          </div>
        </div>
      </div>

      {/* Player Cards Section */}
      {showPlayerCards && (
        <div className="player-cards-section">
          <div className="section-title">Active Players</div>
          <div className="player-cards-grid">
            {activePlayers.length > 0 ? (
              activePlayers.map((player, index) => renderPlayerCard(player, index))
            ) : (
              <div className="no-players">
                <div className="no-players-icon">👥</div>
                <div className="no-players-text">No active players to display</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Winner Modal */}
      {isBingo && (
        <div className="winner-modal-watch">
          <div className="winner-content">
            <div className="winner-title">🎉 Winner!</div>
            <div className="winner-name">{winnerPlayerName}</div>
            <div className="winner-card">Card #{winnerCardNumber}</div>
            <div className="winner-countdown">
              Next game in {winnerCountdown} seconds...
            </div>
          </div>
        </div>
      )}

    
    </div>
  );
};

export default WatchModeScreen;
