import React, { useState, useEffect, useContext, useCallback } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faBars, faTimes, faGamepad, faUser, faHistory, faUsers } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import Toaster from '../components/Toaster';
import LanguageSelector from '../components/LanguageSelector';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import { useTranslation } from 'react-i18next';
import checkPlayerBalance from '../api';
import axios from 'axios';
import { walletApi } from '../services/apiClient';
import { generateFixedCard } from '../helpers/fixedBingoCards';
import config from '../config/api';
import { useAuth } from '../contexts/AuthContext';

const Selections = () => {
  const { t } = useTranslation();
  const {
    selectedNumber,
    setSelectedNumber,
    selectBoard,
    setSelectBoard,
    choosenNumbers,
    setChoosenNumbers,
    gameId,
    setGameId,
    countDown,
    setCountDown,
    roomId,
    setRoomId,
    playerId,
    setPlayerId,
    playerName,
    setPlayerName,
    choosenBoards,
    setChooseBoards,
    toast,
    setToast,
    isToast,
    setIsToast
  } = useContext(BingoContext);
  
  const socket = useContext(SocketContext);
  const navigate = useNavigate();
  const [pickedNumbers, setPickedNumbers] = useState([]);
  const { playersLength, setPlayersLength } = useContext(BingoContext);
  const [isLoading, setIsLoading] = useState(false);
  const [currentCall, setCurrentCall] = useState(null);
  const [gameStatus, setGameStatus] = useState("waiting");
  const [joinError, setJoinError] = useState(false);
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [totalWinAmount, setTotalWinAmount] = useState(0);
  const [isBingo, setIsBingo] = useState(false);
  const [winnerCardNumber, setWinnerCardNumber] = useState(null);
  const [winnerPlayerName, setWinnerPlayerName] = useState(null);
  const [winningCard, setWinningCard] = useState(null);
  const [isSocketConnected, setIsSocketConnected] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const cardsPerPage = 100;
  const [gameInProgress, setGameInProgress] = useState(false);
  const [hasSelectedCard, setHasSelectedCard] = useState(false);
  const [gameStats, setGameStats] = useState({
    totalPlayers: 0,
    totalWinAmount: 0,
    calledNumbersCount: 0,
    totalCalledNumbers: 0
  });
  const { user, token, isAuthenticated } = useAuth();

  // Socket connection handlers
  useEffect(() => {
    const handleConnect = () => {
      console.log('Socket connected');
      setIsSocketConnected(true);
    };

    const handleDisconnect = () => {
      console.log('Socket disconnected');
      setIsSocketConnected(false);
    };

    const handleConnectError = (error) => {
      console.error('Socket connection error:', error);
      setIsSocketConnected(false);
    };

    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('connect_error', handleConnectError);

    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleConnectError);
    };
  }, [socket]);

  // Initialize from authenticated session (Telegram) instead of URL params
  useEffect(() => {
    const sessionPlayerId = user?.telegram_id ? String(user.telegram_id) : null;
    const sessionPlayerName = user?.username || user?.first_name || 'Player';
    const fixedBetAmount = 10; // Always 10 birr

    setPlayerId(sessionPlayerId);
    setRoomId(fixedBetAmount);
    setPlayerName(sessionPlayerName);

    if (sessionPlayerId) {
      socket.emit("playerJoined", { playerId: sessionPlayerId, roomId: fixedBetAmount });

      // Request all player selections
      socket.emit("getAllPlayerSelections", {
        playerId: sessionPlayerId,
        roomId: 10
      });

      // Try to rejoin if there's a previous game in progress
      socket.emit("rejoinGame", {
        playerId: sessionPlayerId,
        roomId: 10
      });
    }

    const handleGameState = (state) => {
      
      if (state.pickedNumbers !== null && state.pickedNumbers && state.pickedNumbers.numbers) {
        setPickedNumbers(state.pickedNumbers.numbers);
        
        // Update total called numbers count
        setGameStats(prevStats => ({
          ...prevStats,
          totalCalledNumbers: state.pickedNumbers.numbers.length
        }));
      }
      
      // Also check for called_numbers in the state
      if (state.called_numbers && Array.isArray(state.called_numbers)) {
        setGameStats(prevStats => ({
          ...prevStats,
          totalCalledNumbers: state.called_numbers.length
        }));
      }
      
      if (state.game_status === "in-progress") {
        if (gameStatus !== "in-progress") {
          setToast("🎮 Game Started! Good luck!");
          setIsToast(true);
        }
        setGameStatus("in-progress");
        setGameInProgress(true);
        
        // Update game statistics
        setGameStats(prevStats => ({
          ...prevStats,
          totalPlayers: state.total_players || prevStats.totalPlayers,
          totalWinAmount: state.win_amount || prevStats.totalWinAmount
        }));
      }
      
      if (state.game_status === "countdown") {
        if (gameStatus !== "countdown") {
          setToast("⏰ Countdown phase started! Game will begin shortly...");
          setIsToast(true);
        }
        setGameStatus("countdown");
      }
      
      if (state.game_status === "waiting") {
        if (gameStatus !== "waiting") {
          setToast("⏳ Game ended. Waiting for next round...");
          setIsToast(true);
        }
        setGameStatus("waiting");
        setGameInProgress(false);
      }
     
      if (state.game_status !== "in-progress") {
        setPlayersLength(state.total_players);
      }
      
      // Update game statistics for all game states
      if (state.total_players !== undefined || state.win_amount !== undefined) {
        setGameStats(prevStats => ({
          ...prevStats,
          totalPlayers: state.total_players || prevStats.totalPlayers,
          totalWinAmount: state.win_amount || prevStats.totalWinAmount
        }));
      }
      
      if (state.count_down !== undefined) {
        const previousCountDown = countDown;
        setCountDown(state.count_down);
        
        if (previousCountDown === 0 && state.count_down > 0) {
          setToast("🚀 Countdown started! Game beginning soon...");
          setIsToast(true);
        }
        
        if (state.count_down === 5) {
          setToast("⚡ 5 seconds left! Get ready!");
          setIsToast(true);
        } else if (state.count_down === 3) {
          setToast("🔥 3 seconds! Almost there!");
          setIsToast(true);
        } else if (state.count_down === 1) {
          setToast("🎯 Final second! Game starting NOW!");
          setIsToast(true);
        }
        // Countdown logic removed - navigation now happens immediately on card selection
      }
    };

    const handlePickedNumbers = (data) => {
      console.log('handlePickedNumbers received:', data);
      if (data.numbers) {
        setPickedNumbers(data.numbers);
      
        
        // Update total called numbers count
        setGameStats(prevStats => ({
          ...prevStats,
          totalCalledNumbers: data.numbers.length
        }));
      }
    };

    const handleGameStatus = (status) => {
      console.log('Game status changed:', status);
      setGameStatus(status);
    };

    const handleBingoWinner = (data) => {
      setWinnerCardNumber(data.winnerCardNumber);
      setWinnerPlayerName(data.winnerPlayerName);
      setWinningCard(data.winningCard);
      setIsBingo(true);
    };

    const handleRejoinSuccess = (data) => {
      setSelectedNumber(data.selectedNumber);
      setSelectBoard(data.selectBoard);
      setChoosenNumbers([data.selectedNumber]);
    };

    const handleRejoinError = (error) => {
      setToast(error.message || 'Failed to rejoin game');
      setIsToast(true);
    };

    const handleAllPlayerSelections = (data) => {
      const selectedNumber = data.players.find(p => p.playerId === playerId)?.selectedNumbers[0];
      // navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
    };
    
    socket.on('gameState', handleGameState);
    socket.on('pickedNumbers', handlePickedNumbers);
    socket.on("gameStatus", handleGameStatus);
    socket.on("bingoWinner", handleBingoWinner);
    socket.on('rejoinSuccess', handleRejoinSuccess);
    socket.on('rejoinError', handleRejoinError);
    socket.on('allPlayerSelections', handleAllPlayerSelections);

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('pickedNumbers', handlePickedNumbers);
      socket.off("gameStatus", handleGameStatus);
      socket.off("bingoWinner", handleBingoWinner);
      socket.off('rejoinSuccess', handleRejoinSuccess);
      socket.off('rejoinError', handleRejoinError);
      socket.off('allPlayerSelections', handleAllPlayerSelections);
    };
  }, [socket, user?.telegram_id, user?.username, user?.first_name, setPlayerId, setPlayerName, setRoomId, gameStatus, countDown, setToast, setIsToast, setPlayersLength, setCountDown, navigate]);

  // Fetch balance when playerId is available
  useEffect(() => {
    if (playerId && token) {
      const fetchBalance = async () => {
        const apiUrl = config.API_BASE_URL;
        try {
          console.log('[BalanceDebug] Fetching balance', { apiUrl, playerId: String(playerId), hasToken: !!token, tokenPrefix: token ? String(token).slice(0, 12) : null });
          const fullUrl = `${apiUrl}wallet/player/${parseInt(playerId)}`;
          console.log('[BalanceDebug] Full URL', { fullUrl, withToken: !!localStorage.getItem('telegram_auth_token') });
          const response = await walletApi.getPlayerWalletByTelegram(playerId);
          const data = response?.data ?? {};
          // Try multiple possible keys used by different backends
          let totalBalance = (
            data?.total_balance ??
            data?.balance ??
            data?.wallet_balance ??
            data?.totalBalance ??
            data?.wallet?.balance
          );
          const numericBalance = Number(totalBalance);
          if (Number.isNaN(numericBalance)) {
            console.log('[BalanceDebug] Could not parse balance from response, defaulting to 0', { data });
            setBalance(0);
          } else {
            console.log('[BalanceDebug] Balance response', { status: response.status, parsed: numericBalance, raw: data });
            setBalance(numericBalance);
          }
          setLoading(false);
        } catch (error) {
          const status = error?.response?.status;
          const data = error?.response?.data;
          const url = `${apiUrl}wallet/player/${parseInt(playerId)}`;
          console.log('[BalanceDebug] Error fetching balance', { url, status, data, message: error?.message });
          setLoading(false);
        }
      };
      fetchBalance();
    }
  }, [playerId, token]);

  // Countdown redirect logic removed - navigation now happens immediately on card selection

  // Update called numbers count when pickedNumbers changes
  useEffect(() => {
    
    setGameStats(prevStats => ({
      ...prevStats,
      calledNumbersCount: pickedNumbers.length,
      totalCalledNumbers: pickedNumbers.length
    }));
  }, [pickedNumbers]);

  // Sidebar functions
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleNavigation = (route) => {
    setIsSidebarOpen(false);
    switch (route) {
      case 'bingo':
        // Already on bingo game page
        break;
      case 'profile':
        navigate('/profile');
        break;
      case 'transactions':
        navigate('/transactions');
        break;
      case 'invited-users':
        navigate('/invited-users');
        break;
      default:
        break;
    }
  };

  // Handle number click
  const handleNumberClick = useCallback(async (number) => {
    if (isLoading || !isSocketConnected) return;

    const isSelected = choosenNumbers.includes(number);
    const isPicked = pickedNumbers.includes(number);
    
    // Check if game is already in progress
    if (gameInProgress) {
      setToast(`🎮 ${t('game.alreadyInProgressWait')}`);
      setIsToast(true);
      return;
    }
    
    if (isPicked) {
      setToast(`Card ${number} is already selected by another player`);
      setIsToast(true);
      return;
    }
    
    // Check balance before proceeding
    try {
      const apiUrl = config.API_BASE_URL;
      const fullUrl = `${apiUrl}wallet/player/${parseInt(playerId)}`;
      console.log('[BalanceDebug] Selection balance check URL', { fullUrl, withToken: !!localStorage.getItem('telegram_auth_token') });
      const response = await walletApi.getPlayerWalletByTelegram(playerId);
      const data = response?.data ?? {};
      let currentBalance = (
        data?.total_balance ??
        data?.balance ??
        data?.wallet_balance ??
        data?.totalBalance ??
        data?.wallet?.balance
      );
      currentBalance = Number(currentBalance);
      if (Number.isNaN(currentBalance)) {
        console.log('[BalanceDebug] Could not parse balance during card select', { data });
        currentBalance = 0;
      }
      
      if (currentBalance < roomId && !isSelected) {
        setToast('Insufficient balance to select this card');
        setIsToast(true);
        return;
      }
      
      // Update balance state
      setBalance(currentBalance);
      
    } catch (error) {
      console.log('[BalanceDebug] Error during balance check on selection', { message: error?.message, status: error?.response?.status, data: error?.response?.data });
      setToast('Error checking balance. Please try again.');
      setIsToast(true);
      return;
    }
    
    if (isSelected) {
      // Unselect - emit leave event
      const leaveData = {
        playerId: playerId,
        gameId: gameId || 'default',
        roomId: roomId
      };
      
      console.log('Emitting leave with data:', leaveData);
      socket.emit('leave', leaveData);
      
      setChoosenNumbers(prev => prev.filter(n => n !== number));
      setSelectedNumber(null);
      setSelectBoard(null);
      setChooseBoards([]);
      setHasSelectedCard(false); // Set to false when unselecting
      
      setToast(`Card ${number} unselected. Left the game.`);
      setIsToast(true);
    } else {
      // Select card and wait for countdown
      setChoosenNumbers([number]);
      setSelectedNumber(number);
      setHasSelectedCard(true); // Set to true when selecting
      
      // Generate card data using fixed card system
      const generateCard = (cardNumber) => {
        return generateFixedCard(cardNumber);
      };

      const card = generateCard(number);
      setSelectBoard(card);
      setChooseBoards([card]);
      
      // Emit join game event
      const joinData = {
        playerId: playerId,
        gameId: gameId || 'default',
        selectedNumber: number,
        roomId: roomId,
        selectBoard: card,
        numberOfBoards: 1
      };
      
      console.log('Emitting joinGame with data:', joinData);
      socket.emit('joinGame', joinData);
      
      setToast(`Card ${number} selected! Waiting for countdown to reach zero...`);
      setIsToast(true);
      
      // Navigation will happen automatically when countdown reaches 0
      // No immediate navigation - user stays on selection page
    }
  }, [isLoading, isSocketConnected, choosenNumbers, pickedNumbers, gameInProgress, balance, roomId, playerId, gameId, socket, setChoosenNumbers, setSelectedNumber, setSelectBoard, setChooseBoards, setHasSelectedCard, setToast, setIsToast, playerName, navigate]);

  // Handle navigation only when countdown reaches 0
  useEffect(() => {
    if (countDown === 0 && hasSelectedCard && selectedNumber && gameStatus === "in-progress") {
      // Check balance before navigation
      if (balance >= parseInt(roomId)) {
        console.log("✅ Countdown reached zero - navigating to play screen");
        navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
      } else {
        console.log("❌ Insufficient balance for navigation");
        setToast("Insufficient balance to join the game. Please deposit more.");
        setIsToast(true);
      }
    }
  }, [countDown, hasSelectedCard, selectedNumber, gameStatus, balance, roomId, playerId, playerName, navigate, setToast, setIsToast]);

  // Pagination logic
  const totalCards = 800;
  const totalPages = Math.ceil(totalCards / cardsPerPage);
  
  const getCurrentPageNumbers = () => {
    const startIndex = (currentPage - 1) * cardsPerPage;
    const endIndex = Math.min(startIndex + cardsPerPage, totalCards);
    return Array.from({ length: endIndex - startIndex }, (_, i) => startIndex + i + 1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  return (
    <>
      {isToast && <Toaster message={toast} />}
      {loading && (
        <div className="fancy-loading-container">
          <div className="loading-background">
            <div className="loading-particles">
              {[...Array(20)].map((_, i) => (
                <div key={i} className={`particle particle-${i + 1}`}></div>
              ))}
            </div>
          </div>
          
          <div className="loading-content">
            <div className="loading-logo">
              <div className="logo-text">LIYU</div>
              <div className="logo-subtitle">BINGO</div>
            </div>
            
            <div className="loading-spinner-container">
              <div className="fancy-spinner">
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
              </div>
            </div>
            
            <div className="loading-text-container">
              <div className="loading-text">{t('common.loading')}</div>
              <div className="loading-dots">
                <span className="dot">.</span>
                <span className="dot">.</span>
                <span className="dot">.</span>
              </div>
            </div>
            
            <div className="loading-progress">
              <div className="progress-bar">
                <div className="progress-fill"></div>
              </div>
            </div>
          </div>
        </div>
      )}

{isBingo && (
  <div className="bingo-winner-overlay">
    <div className="bingo-winner-card" style={{ maxHeight: '80vh', overflowY: 'auto', width: '100%', maxWidth: 480 }}>
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
      }}>
        {winnerPlayerName === playerName ? (
          <>🎉 Congratulations! You won! 🎉</>
        ) : (
          <>ስም : {winnerPlayerName} is Winner</>
        )}
      </p>
     
<div className="winning-card">
  <div className="winning-card-row">
    {["B", "I", "N", "G", "O"].map((letter, index) => (
      <div key={index} className="winning-card-cell">
        <span>{letter}</span>
      </div>
    ))}
  </div>
              {winningCard && winningCard[0] && winningCard[0].map((_, rowIndex) => (
    <div key={rowIndex} className="winning-card-row">
      {winningCard.map((row, colIndex) => {
        const cell = row[rowIndex];
        const rowComplete = winningCard.every(r => r[rowIndex].marked);
        const colComplete = winningCard[colIndex].every(c => c.marked);
                    const diagonalComplete = rowIndex === colIndex && winningCard.every((r, i) => r[i].marked);
                    const reverseDiagonalComplete = rowIndex + colIndex === 4 && winningCard.every((r, i) => r[4 - i].marked);
                    const fourCornersComplete = winningCard[0][0].marked && winningCard[0][4].marked && winningCard[4][0].marked && winningCard[4][4].marked;
                    const fourEdgesComplete = winningCard[0][2].marked && winningCard[2][0].marked && winningCard[2][4].marked && winningCard[4][2].marked;

        let bgColor = "white";
                    if (rowComplete || colComplete || diagonalComplete || reverseDiagonalComplete || fourCornersComplete || fourEdgesComplete) {
                      bgColor = "green";
        } else if (cell.marked) {
                      bgColor = "red";
        }

        return (
                      <div key={colIndex} className="winning-card-cell" style={{ backgroundColor: bgColor }}>
            <span>{cell.number}</span>
          </div>
        );
      })}
    </div>
  ))}
</div>
      <div className="choosen-numbers">
        <span className="choosen-number">የካርቴላ ቁጥር :- {winnerCardNumber}</span>
      </div>
    </div>
  </div>
)}

      {!loading && (
        <div className="konjo-selections-container">
          {/* Header */}
          
          <div className="konjo-header">
          <div className="konjo-header-left">
              <div className="hamburger-menu" onClick={toggleSidebar}>
                <FontAwesomeIcon icon={faBars} />
              </div>
              <div className="konjo-logo">Liyu</div>
            </div>
            
            <div className="konjo-header-right">
              {/* Connection Status Indicator */}
              <div className="connection-indicator">
                <div className={`connection-dot ${isSocketConnected ? 'connected' : 'disconnected'}`}></div>
                <span className="connection-text">
                  {isSocketConnected ? t('game.live') : t('game.connecting')}
                </span>
              </div>
              
              {/* Game Stats */}
              <div className="header-stats">
                <div className="header-stat">
                  <span className="stat-value">{gameStats.totalPlayers}</span>
                </div>
                <div className="header-stat">
                  <span className="stat-value">{gameStats.totalWinAmount.toFixed(0)} ETB</span>
                </div>
              </div>
              
              {/* Countdown */}
              {countDown > 0 && (
                <div className="header-countdown">
                  <div className="countdown-circle">
                    <span className="countdown-number">{countDown}</span>
                  </div>
                </div>
              )}
              
              <div className="balance-button">
                <span className="balance-amount">{(() => {
                  const parsed = parseInt(balance);
                  const isNum = !Number.isNaN(parsed);
                  if (!isNum) {
                    console.log('[BalanceDebug] Rendering NA balance', { balance, parsed });
                  }
                  return isNum ? parsed : 'NA';
                })()} ETB</span>
                <div className="user-icon">👤</div>
              </div>
              
              {/* Interactive Live Indicator */}
              <div className="live-indicator interactive" onClick={() => {
                setToast("🎮 Live game in progress! Join now!");
                setIsToast(true);
              }}>
                <div className="live-dot"></div>
                <span className="live-text">LIVE</span>
                <div className="live-pulse-ring"></div>
              </div>
            </div>
          </div>

          {/* Sub-header */}
          <div className="konjo-sub-header">
            
            <div className="info-buttons">
              <div className="info-button">{t('game.betAmount')} {roomId} {t('currency.birr')}</div>
            </div>
            <div className="action-buttons">
              <button 
                className="start-button"
                onClick={() => {
                  if (hasSelectedCard && selectedNumber) {
                    console.log('[StartDebug] Start clicked', { hasSelectedCard, selectedNumber, balance, roomId, playerId, playerName });
                    if (Number(balance) >= parseInt(roomId)) {
                      navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
                    } else {
                      console.log('[StartDebug] Blocked: insufficient balance', { balance, required: parseInt(roomId) });
                      setToast(t('game.insufficientBalance'));
                      setIsToast(true);
                    }
                  } else {
                    console.log('[StartDebug] Blocked: no card selected', { hasSelectedCard, selectedNumber });
                    setToast(t('game.cardNotSelected'));
                    setIsToast(true);
                  }
                }}
                disabled={!hasSelectedCard || !selectedNumber}
              >
                🚀 {t('game.joinGame')}
              </button>
              <button 
                className="exit-button"
                onClick={() => {
                  if (hasSelectedCard && selectedNumber) {
                    // Leave the game if user has selected a card
                    const leaveData = {
                      playerId: playerId,
                      gameId: gameId || 'default',
                      roomId: roomId
                    };
                    socket.emit('leave', leaveData);
                    
                    // Reset selection
                    setChoosenNumbers([]);
                    setSelectedNumber(null);
                    setSelectBoard(null);
                    setChooseBoards([]);
                    setHasSelectedCard(false);
                    
                    setToast("Left the game successfully!");
                    setIsToast(true);
                  } else {
                    // Just navigate back to main menu
                    navigate('/');
                  }
                }}
              >
                🚪 Exit
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="konjo-main-content">
           
            {/* Game Status Indicator */}
            {gameInProgress && (
              <div className="game-status-indicator">
                <div className="status-icon">🎮</div>
                <div className="status-text">{t('game.alreadyInProgress')}</div>
                <div className="status-subtext">{t('game.waitForNextRound')}</div>
              </div>
            )}
           
            {/* Number Grid 1-800 with Pagination */}
            <div className="pagination-info">
              <div className="page-info">
                Showing cards {((currentPage - 1) * cardsPerPage) + 1} - {Math.min(currentPage * cardsPerPage, totalCards)} of {totalCards}
              </div>
            </div>
            
            <div className="konjo-number-grid">
              {getCurrentPageNumbers().map((number) => {
                const isSelected = choosenNumbers.includes(number);
                const isPicked = pickedNumbers.includes(number);
                const isDisabled = isPicked || !isSocketConnected || (balance < roomId && !isSelected) || gameInProgress;

                return (
                  <button
                    key={number}
                    className={`konjo-number-cell ${isPicked ? 'picked' : ''} ${isSelected ? 'selected' : ''} ${isDisabled ? 'disabled' : ''}`}
                    onClick={() => handleNumberClick(number)}
                    disabled={isDisabled}
                  >
                    {number}
                  </button>
                );
              })}
            </div>

            {/* Pagination Controls */}
            <div className="pagination-controls">
              <button 
                className="pagination-btn"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              
              <div className="pagination-numbers">
                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <span key={`ellipsis-${index}`} className="pagination-ellipsis">...</span>
                  ) : (
                    <button
                      key={page}
                      className={`pagination-number ${currentPage === page ? 'active' : ''}`}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </button>
                  )
                ))}
              </div>
              
              <button 
                className="pagination-btn"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>

            {/* Selected Card Preview Modal (Enhanced) */}
            {selectedNumber && (
              <div 
                className="konjo-card-preview show"
                onClick={(e) => {
                  if (e.target === e.currentTarget) {
                    setSelectedNumber(null);
                  }
                }}
                style={{
                  backdropFilter: 'blur(2px)',
                }}
              >
                <div className="modal-content" style={{
                  background: 'linear-gradient(180deg, #0f1224 0%, #1b1f3b 100%)',
                  borderRadius: 16,
                  boxShadow: '0 12px 40px rgba(0,0,0,0.35), inset 0 0 0 1px rgba(255,255,255,0.06)',
                  overflow: 'hidden'
                }}>
                  {/* Header */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 16px',
                    borderBottom: '1px solid rgba(255,255,255,0.08)'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10
                    }}>
                      <div style={{
                        width: 36,
                        height: 36,
                        borderRadius: 8,
                        background: 'radial-gradient(120% 120% at 10% 10%, #ff799a 0%, #7a5cff 55%, #2dd4bf 100%)',
                        boxShadow: '0 0 20px rgba(122,92,255,0.45)'
                      }} />
                      <div style={{ color: '#E7E9F7', fontWeight: 700, fontSize: 16 }}>
                        {t('game.preview')} • #{selectedNumber}
                      </div>
                    </div>
                    <button 
                      onClick={() => setSelectedNumber(null)}
                      aria-label="Close bingo card"
                      style={{
                        background: 'transparent',
                        color: '#9aa0c3',
                        border: 'none',
                        fontSize: 22,
                        lineHeight: '22px',
                        cursor: 'pointer'
                      }}
                    >
                      ×
                    </button>
                  </div>

                  {/* Body */}
                  <div className="modal-body" style={{ padding: 16 }}>
                    {/* Fancy card frame */}
                    <div style={{
                      background: 'linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%)',
                      borderRadius: 14,
                      padding: 12,
                      boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.06), 0 8px 28px rgba(0,0,0,0.25)'
                    }}>
                      {/* BINGO header chips */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6, marginBottom: 8 }}>
                        {['B','I','N','G','O'].map((l, i) => (
                          <div key={i} style={{
                            textAlign: 'center',
                            color: '#111827',
                            fontWeight: 800,
                            letterSpacing: 1.5,
                            borderRadius: 10,
                            padding: '8px 0',
                            background: 'linear-gradient(180deg, #fdfbfb 0%, #ebeef8 100%)',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                          }}>{l}</div>
                        ))}
                      </div>

                      {/* Numbers grid */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
                        {selectBoard.map((col, colIndex) => (
                          <div key={colIndex} style={{ display: 'grid', gap: 6 }}>
                            {col.map((num, rowIndex) => (
                              <div
                                key={`${colIndex}-${rowIndex}`}
                                style={{
                                  height: 48,
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  borderRadius: 10,
                                  color: num === '*' ? '#0f172a' : '#e5e7eb',
                                  fontWeight: 700,
                                  background: num === '*'
                                    ? 'linear-gradient(180deg, #a7f3d0 0%, #34d399 100%)'
                                    : 'radial-gradient(120% 120% at 20% 10%, rgba(124,58,237,0.9) 0%, rgba(79,70,229,0.85) 55%, rgba(59,130,246,0.8) 100%)',
                                  boxShadow: num === '*'
                                    ? '0 4px 12px rgba(16,185,129,0.35)'
                                    : '0 4px 12px rgba(99,102,241,0.35)'
                                }}
                              >
                                {num === '*' ? (
                                  <div style={{ textAlign: 'center', lineHeight: 1.1 }}>
                                    <div style={{ fontSize: 10, fontWeight: 800 }}>FREE</div>
                                    <div style={{ fontSize: 10, opacity: 0.9 }}>SPACE</div>
                                  </div>
                                ) : (
                                  <span style={{ fontSize: 16 }}>{num}</span>
                                )}
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Footer actions */}
                    <div style={{ display: 'flex', gap: 12, marginTop: 14 }}>
                      <button 
                        className="bingo-start-button"
                        onClick={() => {
                          if (hasSelectedCard && selectedNumber) {
                            if (Number(balance) >= parseInt(roomId)) {
                              navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
                            } else {
                              setToast(t('game.insufficientBalance'));
                              setIsToast(true);
                            }
                          } else {
                            setToast(t('game.cardNotSelected'));
                            setIsToast(true);
                          }
                        }}
                        style={{
                          flex: 1,
                          background: 'linear-gradient(180deg, #22d3ee 0%, #3b82f6 100%)',
                          border: 'none',
                          color: 'white',
                          borderRadius: 10,
                          padding: '12px 14px',
                          fontWeight: 800,
                          boxShadow: '0 6px 16px rgba(56,189,248,0.35)',
                          cursor: 'pointer'
                        }}
                      >
                        🚀 {t('game.startGame')}
                      </button>
                      <button
                        onClick={() => setSelectedNumber(null)}
                        style={{
                          background: 'transparent',
                          border: '1px solid rgba(255,255,255,0.15)',
                          color: '#c7c9e2',
                          borderRadius: 10,
                          padding: '12px 14px',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        ✖ {t('common.close') || 'Close'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Countdown removed - navigation happens immediately on card selection */}
                  </div>

          
        </div>
      )}

      {/* Sidebar */}
      {isSidebarOpen && (
        <>
          <div className="sidebar-overlay" onClick={toggleSidebar}></div>
          <div className="sidebar">
            <div className="sidebar-header">
              <div className="sidebar-title">{t('navigation.menu')}</div>
              <button className="sidebar-close" onClick={toggleSidebar}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="sidebar-content">
              <div className="sidebar-menu">
                <div className="sidebar-item" onClick={() => handleNavigation('bingo')}>
                  <FontAwesomeIcon icon={faGamepad} className="sidebar-icon" />
                  <span>{t('navigation.bingoGame')}</span>
                </div>
                <div className="sidebar-item" onClick={() => handleNavigation('profile')}>
                  <FontAwesomeIcon icon={faUser} className="sidebar-icon" />
                  <span>{t('navigation.profile')}</span>
                </div>
                <div className="sidebar-item" onClick={() => handleNavigation('transactions')}>
                  <FontAwesomeIcon icon={faHistory} className="sidebar-icon" />
                  <span>{t('navigation.transactionHistory')}</span>
                </div>
                <div className="sidebar-item" onClick={() => handleNavigation('invited-users')}>
                  <FontAwesomeIcon icon={faUsers} className="sidebar-icon" />
                  <span>{t('navigation.invitedUsers')}</span>
                </div>
                <div className="sidebar-language-section">
                  <div className="sidebar-language-title">{t('navigation.language')}</div>
                  <LanguageSelector />
                </div>
              </div>
            </div>
        </div>
        </>
      )}
    </>
  );
};

export default Selections;