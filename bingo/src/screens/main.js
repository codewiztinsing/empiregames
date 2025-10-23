import React, { useState, useContext, useEffect, useCallback, useMemo } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog, faVolumeMute, faVolumeUp, faSignOutAlt, faSync } from '@fortawesome/free-solid-svg-icons';
import { generateFixedCard } from '../helpers/fixedBingoCards';
import { hasBingo, checkBingoPatterns, markCardNumber } from '../helpers/fixedBingoCards';
import { useTranslation } from 'react-i18next';
import LanguageSelector from '../components/LanguageSelector';

const PlayingBoard = () => {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // Get URL parameters
  const autoPlay = searchParams.get('autoPlay') !== 'false'; // Default to true unless explicitly false
  const watchMode = searchParams.get('watchMode') === 'true';
  
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

  // Watch mode and auto-play state
  const [isWatchMode, setIsWatchMode] = useState(watchMode);
  const [isAutoPlayDisabled, setIsAutoPlayDisabled] = useState(!autoPlay);

  // Handle watch mode initialization
  useEffect(() => {
    if (isWatchMode) {
      console.log("🎮 Watch mode enabled - user is observing the game");
      toast.success("🎮 Watch Mode: You're observing the current game");
    }
    if (isAutoPlayDisabled) {
      console.log("🎮 Auto-play disabled - user needs to manually select cards");
      toast.info("🎮 Auto-play disabled - Select your cards manually");
    }
  }, [isWatchMode, isAutoPlayDisabled]);

  // Game state
  const [gameState, setGameState] = useState({
    calledNumbers: [],
    lastBall: null,
    totalCalledNumbers: 0,
    selectedCell: new Set(),
    isBingo: false,
    isDisqualified: false,
    winningCard: null,
    winner: null,
    winnerCardNumber: null,
    winnerPlayerName: null,
    markedCells: [],
    firstBoardLost: false,
    hasSufficientBalance: true, // Track if user has sufficient balance
    winAmount: 0,
    totalWinAmount: 0,
    totalPlayers: 0,
    recentCalledNumbers: ['*', '*', '*'],
    winnerCountdown: 5,
    isMuted: false,
    autoPlay: false,
    gameCountdown: 0,
    gameStatus: 'waiting',
    showDepositReminder: false, // Control deposit reminder popup
    depositReminderDismissed: false, // Track if user dismissed reminder
  });

  // Destructure for easier access
  const {
    calledNumbers,
    lastBall,
    totalCalledNumbers,
    selectedCell,
    isBingo,
    isDisqualified,
    winningCard,
    winner,
    winnerCardNumber,
    winnerPlayerName,
    markedCells,
    firstBoardLost,
    winAmount,
    totalWinAmount,
    totalPlayers,
    recentCalledNumbers,
    winnerCountdown,
    isMuted,
    autoPlay,
    gameCountdown,
    gameStatus,
    showDepositReminder,
    depositReminderDismissed
  } = gameState;

  // Debug log for autoPlay state
  console.log('Current autoPlay state:', autoPlay);

  // Computed values
  const displayedTotalPlayers = useMemo(() => totalPlayers || 0, [totalPlayers]);
  const displayedWinAmount = useMemo(() => 
    (displayedTotalPlayers * (roomId || 0) * 0.78) || 0, 
    [displayedTotalPlayers, roomId]
  );

  // Helper functions
  const updateGameState = useCallback((updates) => {
    setGameState(prevState => ({ ...prevState, ...updates }));
  }, []);

  const getElementIdForNumber = useCallback((number) => {
    if (number >= 1 && number <= 15) return `B${number}`;
    if (number >= 16 && number <= 30) return `I${number}`;
    if (number >= 31 && number <= 45) return `N${number}`;
    if (number >= 46 && number <= 60) return `G${number}`;
    if (number >= 61 && number <= 75) return `O${number}`;
    return null;
  }, []);

  const animateNumber = useCallback((element, duration) => {
    if (!element) return;
    
    element.style.transform = 'scale(1.2)';
    element.style.transition = `transform ${duration}ms ease-in-out`;
    
    setTimeout(() => {
      element.style.transform = 'scale(1)';
    }, duration / 2);
  }, []);

  // Initialize component with URL parameters
  useEffect(() => {
    const initializeFromURL = () => {
    const queryParams = new URLSearchParams(window.location.search);
    const urlPlayerId = queryParams.get('playerId');
    const urlRoomId = '10'; // Force 10 birr always
    const urlPlayerName = queryParams.get('playerName');
    const urlSelectedNumber = queryParams.get('selectedNumber');
    const urlHasSufficientBalance = queryParams.get('hasSufficientBalance') === 'true';
    
    if (urlPlayerId) setPlayerId(urlPlayerId);
    const roomIdValue = 10;
    setRoomId(roomIdValue);
    setGameId(roomIdValue); // Server uses roomId as game key
    if (urlPlayerName && urlPlayerName !== 'null') setPlayerName(urlPlayerName);
    
    // Set balance status
    setGameState(prev => ({ ...prev, hasSufficientBalance: urlHasSufficientBalance }));
    if (urlSelectedNumber) {
      const selectedNum = parseInt(urlSelectedNumber);
      setSelectedNumber(selectedNum);
        // Generate card data using fixed card system
        const generateCard = (cardNumber) => {
          return generateFixedCard(cardNumber);
        };
        setSelectBoard(generateCard(selectedNum));
      }
    };

    initializeFromURL();
  }, [setPlayerId, setRoomId, setPlayerName, setSelectedNumber, setSelectBoard]);

  const socket = useContext(SocketContext);
  const navigate = useNavigate();
  
  // Socket connection state
  const [isSocketConnected, setIsSocketConnected] = useState(false);

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

  // Keep totalCalledNumbers in sync with calledNumbers length
  useEffect(() => {
    updateGameState(prevState => ({
      ...prevState,
      totalCalledNumbers: prevState.calledNumbers.length
    }));
  }, [calledNumbers.length, updateGameState]);

  // Socket event handlers
  const handleGameState = useCallback((data) => {
    try {
      const calledNumber = data?.lastBall?.combined?.split("-")[1];
      
      // Handle game completion
      if (data.called_numbers?.length === 75) {
        setToast("All 75 numbers have been called! Please select new cards for the next game.");
        setIsToast(true);
        navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
        window.location.reload();
        return;
      }

      // Update win amount and total players
      if (data.win_amount) {
        updateGameState({
          winAmount: data.win_amount,
          totalPlayers: data.total_players
        });
      }
      
      // Handle called numbers
      if (data.called_numbers && Array.isArray(data.called_numbers)) {
        const calledNumbersArray = data.called_numbers.map(ball => ball.number);
        updateGameState({ 
          calledNumbers: calledNumbersArray,
          totalCalledNumbers: calledNumbersArray.length
        });
        
        // Animate the last called number
        if (calledNumber) {
          setTimeout(() => {
            const elementId = getElementIdForNumber(parseInt(calledNumber));
            const element = document.getElementById(elementId);
            if (element) {
              animateNumber(element, 2000);
            }
          }, 100);
        }
      } else if (calledNumber) {
        // Fallback for single number updates
        updateGameState(prevState => ({
          calledNumbers: [...prevState.calledNumbers, parseInt(calledNumber)],
          totalCalledNumbers: prevState.calledNumbers.length + 1
        }));
        
          setTimeout(() => {
            const elementId = getElementIdForNumber(parseInt(calledNumber));
            const element = document.getElementById(elementId);
            if (element) {
              animateNumber(element, 2000);
            }
          }, 100);
      }
      
      updateGameState({ lastBall: data.lastBall });
    } catch (error) {
      console.error('Error handling game state:', error);
    }
  }, [updateGameState, getElementIdForNumber, animateNumber, setToast, setIsToast, navigate, playerId, roomId, playerName]);

  const handleBingoWinner = useCallback((data) => {
    try {
      console.log('Bingo winner received:', data);
      console.log('Winning card data:', data.winningCard);
      
      updateGameState({
        isBingo: true,
        winnerCardNumber: data.winnerCardNumber,
        winnerPlayerName: data.winnerPlayerName,
        winningCard: data.winningCard
      });
    } catch (error) {
      console.error('Error handling bingo winner:', error);
    }
  }, [updateGameState]);

  const handleFalseBingo = useCallback((data) => {
    try {
      console.log('False bingo received:', data);
      setToast('❌ False Bingo! You are disqualified for this round.');
      setIsToast(true);
      updateGameState({
        isDisqualified: true
      });
    } catch (error) {
      console.error('Error handling false bingo:', error);
    }
  }, [updateGameState, setToast, setIsToast]);

  const handleDisqualified = useCallback((data) => {
    try {
      console.log('Disqualified received:', data);
      setToast('❌ You are disqualified for this round due to false bingo.');
      setIsToast(true);
      updateGameState({
        isDisqualified: true
      });
    } catch (error) {
      console.error('Error handling disqualified:', error);
    }
  }, [updateGameState, setToast, setIsToast]);

  const handleGameStateUpdate = useCallback((data) => {
    try {
      console.log('Game state update received:', data);
      
      // Update countdown if provided
      if (data.count_down !== undefined) {
        updateGameState({
          gameCountdown: data.count_down
        });
        setCountDown(data.count_down);
      }
      
      // Update game status if provided
      if (data.game_status) {
        updateGameState({
          gameStatus: data.game_status
        });
      }
      
      // Update total players if provided
      if (data.total_players !== undefined) {
        updateGameState({
          totalPlayers: data.total_players
        });
      }
      
      // Update called numbers if provided
      if (data.pickedNumbers && data.pickedNumbers.numbers) {
        updateGameState({
          calledNumbers: data.pickedNumbers.numbers,
          totalCalledNumbers: data.pickedNumbers.numbers.length
        });
      }
      
    } catch (error) {
      console.error('Error handling game state update:', error);
    }
  }, [updateGameState, setCountDown]);

  // Function to determine winning condition
  const getWinningCondition = useCallback((card) => {
    if (!card || !card[0]) return 'Unknown';
    
    // Check rows
    for (let row = 0; row < 5; row++) {
      if (card.every(col => col[row].marked)) {
        return `Row ${row + 1} Complete`;
      }
    }
    
    // Check columns
    for (let col = 0; col < 5; col++) {
      if (card[col].every(cell => cell.marked)) {
        return `Column ${String.fromCharCode(66 + col)} Complete`;
      }
    }
    
    // Check diagonal (top-left to bottom-right)
    if (card.every((col, i) => col[i].marked)) {
      return 'Diagonal Complete';
    }
    
    // Check reverse diagonal (top-right to bottom-left)
    if (card.every((col, i) => col[4 - i].marked)) {
      return 'Reverse Diagonal Complete';
    }
    
    // Check four corners
    if (card[0][0].marked && card[0][4].marked && card[4][0].marked && card[4][4].marked) {
      return 'Four Corners Complete';
    }
    
    // Check four edges (cross pattern)
    if (card[0][2].marked && card[2][0].marked && card[2][4].marked && card[4][2].marked) {
      return 'Four Edges Complete';
    }
    
    return 'Pattern Complete';
  }, []);

  // Function to determine which cells are part of the winning pattern
  const getWinningPattern = useCallback((card) => {
    if (!card || !card[0]) return [];
    
    const winningCells = [];
    
    // Check rows
    for (let row = 0; row < 5; row++) {
      if (card.every(col => col[row].marked)) {
        for (let col = 0; col < 5; col++) {
          winningCells.push({ row, col });
        }
        return winningCells;
      }
    }
    
    // Check columns
    for (let col = 0; col < 5; col++) {
      if (card[col].every(cell => cell.marked)) {
        for (let row = 0; row < 5; row++) {
          winningCells.push({ row, col });
        }
        return winningCells;
      }
    }
    
    // Check diagonal (top-left to bottom-right)
    if (card.every((col, i) => col[i].marked)) {
      for (let i = 0; i < 5; i++) {
        winningCells.push({ row: i, col: i });
      }
      return winningCells;
    }
    
    // Check reverse diagonal (top-right to bottom-left)
    if (card.every((col, i) => col[4 - i].marked)) {
      for (let i = 0; i < 5; i++) {
        winningCells.push({ row: i, col: 4 - i });
      }
      return winningCells;
    }
    
    // Check four corners
    if (card[0][0].marked && card[0][4].marked && card[4][0].marked && card[4][4].marked) {
      winningCells.push({ row: 0, col: 0 });
      winningCells.push({ row: 0, col: 4 });
      winningCells.push({ row: 4, col: 0 });
      winningCells.push({ row: 4, col: 4 });
      return winningCells;
    }
    
    return winningCells;
  }, []);

  // Function to render winning card properly
  const renderWinningCard = useCallback((card) => {
    console.log('Rendering winning card:', card);
    
    if (!card || !card[0]) {
      console.log('No card data available');
      return <div className="no-card-data">No winning card data available</div>;
    }
    
    console.log('Card structure:', {
      hasCard: !!card,
      cardLength: card.length,
      firstRowLength: card[0]?.length,
      sampleCell: card[0]?.[0]
    });
    
    const winningPattern = getWinningPattern(card);
    console.log('Winning pattern:', winningPattern);
    
    return (
      <div className="winning-card">
        {/* Header Row */}
        <div className="winning-card-row">
          {["B", "I", "N", "G", "O"].map((letter, index) => (
            <div key={index} className="winning-card-cell winning-card-header">
              <span className="bingo-letter">{letter}</span>
            </div>
          ))}
        </div>
        
        {/* Number Rows */}
        {card[0].map((_, rowIndex) => (
          <div key={rowIndex} className="winning-card-row">
            {card.map((col, colIndex) => {
              const cell = col[rowIndex];
              const isMarked = cell.marked;
              const isWinningCell = winningPattern.some(wc => wc.row === rowIndex && wc.col === colIndex);
              
              // Get the actual number for this cell position
              let displayNumber;
              if (cell.number === '*') {
                displayNumber = 'FREE';
              } else if (cell.number !== undefined && cell.number !== null) {
                displayNumber = cell.number;
              } else {
                // If number is missing, try to get it from the card structure
                // This is a fallback for incomplete card data
                displayNumber = '?';
              }
              
              console.log(`Cell [${colIndex}][${rowIndex}]:`, { 
                cell, 
                number: cell.number, 
                displayNumber,
                marked: cell.marked,
                isMarked, 
                isWinningCell 
              });
              
              let cellClass = 'winning-card-cell';
              if (isWinningCell) {
                cellClass += ' winning-complete';
              } else if (isMarked) {
                cellClass += ' winning-marked';
              }
              
              return (
                <div 
                  key={colIndex} 
                  className={cellClass}
                >
                  <span>{displayNumber}</span>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    );
  }, [getWinningPattern]);

  // Socket event bindings
  useEffect(() => {
    if (!socket) return;

    socket.on('gameState', handleGameState);
    socket.on('gameState', handleGameStateUpdate); // Listen for countdown updates
    socket.on('bingoWinner', handleBingoWinner);
    socket.on('falseBingo', handleFalseBingo);
    socket.on('disqualified', handleDisqualified);

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('gameState', handleGameStateUpdate);
      socket.off('bingoWinner', handleBingoWinner);
      socket.off('falseBingo', handleFalseBingo);
      socket.off('disqualified', handleDisqualified);
    };
  }, [socket, handleGameState, handleGameStateUpdate, handleBingoWinner, handleFalseBingo, handleDisqualified]);

  const handleCellClick = useCallback((number) => {
    try {
      if (number === '*' || isBingo || isDisqualified) return;
      
      console.log('Cell clicked:', number);
      
      setGameState(prevState => {
        const newSelectedCell = new Set(prevState.selectedCell);
        if (newSelectedCell.has(number)) {
          newSelectedCell.delete(number);
          console.log('Removed number:', number);
        } else {
          newSelectedCell.add(number);
          console.log('Added number:', number);
        }
        
        console.log('New selectedCell:', newSelectedCell);
        return { ...prevState, selectedCell: newSelectedCell };
      });
    } catch (error) {
      console.error('Error handling cell click:', error);
    }
  }, [isBingo, isDisqualified]);

  const handleBingo = useCallback((board, cardNumber) => {
    try {
      console.log('handleBingo called with:', { board, cardNumber, isBingo, isDisqualified });
      console.log('Socket status:', { socket: !!socket, connected: socket?.connected });
      
      if (!socket) {
        console.error('Socket not available');
        return;
      }
      
      if (!board || !cardNumber || isBingo || isDisqualified || !gameState.hasSufficientBalance) {
        console.log('Bingo call blocked:', { 
          hasBoard: !!board, 
          hasCardNumber: !!cardNumber, 
          isBingo, 
          isDisqualified,
          hasSufficientBalance: gameState.hasSufficientBalance
        });
        if (!gameState.hasSufficientBalance) {
          setToast('💰 Bingo disabled - Insufficient balance. Please deposit to enable bingo.');
          setIsToast(true);
        }
        return;
      }
      
      console.log('Emitting bingo event to server...');
      socket.emit('bingo', {
        playerId,
        gameId,
        roomId, // Add roomId for proper game lookup
        boardNumber: cardNumber,
        board,
        playerName
      });
      
      console.log('Bingo event emitted successfully');
    } catch (error) {
      console.error('Error handling bingo:', error);
    }
  }, [socket, playerId, gameId, roomId, isBingo, isDisqualified, playerName, gameState.hasSufficientBalance, setToast, setIsToast]);

  const handleCloseWinner = useCallback(() => {
    try {
      updateGameState({
        isBingo: false,
        winnerCardNumber: null,
        winnerPlayerName: null,
        winningCard: null
      });
      
      // Navigate to home screen with all query parameters
      navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
    } catch (error) {
      console.error('Error closing winner:', error);
    }
  }, [updateGameState, navigate, playerId, roomId, playerName]);

  // Deposit reminder handlers
  const handleCloseDepositReminder = useCallback(() => {
    setGameState(prev => ({ ...prev, showDepositReminder: false }));
  }, []);

  const handleDismissDepositReminder = useCallback(() => {
    setGameState(prev => ({ ...prev, showDepositReminder: false, depositReminderDismissed: true }));
  }, []);

  const handleDepositNow = useCallback(() => {
    setGameState(prev => ({ ...prev, showDepositReminder: false }));
    setToast(`💰 ${t('deposit.redirectingToDeposit')}`);
    setIsToast(true);
    // Here you would typically navigate to a deposit page or open a deposit modal
    // For now, we'll just show a message
  }, [setToast, setIsToast, t]);

  const handleLeaveGame = useCallback(() => {
    try {
      navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
    } catch (error) {
      console.error('Error leaving game:', error);
    }
  }, [navigate, playerId, roomId, playerName]);

  const handleRefresh = useCallback(() => {
    try {
      window.location.reload();
    } catch (error) {
      console.error('Error refreshing:', error);
    }
  }, []);

  const toggleMute = useCallback(() => {
    updateGameState(prevState => ({ isMuted: !prevState.isMuted }));
  }, [updateGameState]);

  const toggleAutoPlay = useCallback(() => {
    console.log('toggleAutoPlay clicked, current autoPlay:', autoPlay);
    
    // Check if user has sufficient balance
    if (!gameState.hasSufficientBalance) {
      setToast('💰 Autoplay disabled - Insufficient balance. Please deposit to enable autoplay.');
      setIsToast(true);
      return;
    }
    
    const newAutoPlayState = !autoPlay;
    console.log('newAutoPlayState:', newAutoPlayState);
    
    // Direct state update for testing
    setGameState(prevState => {
      console.log('setGameState called, prevState:', prevState);
      const newState = { ...prevState, autoPlay: newAutoPlayState };
      console.log('newState:', newState);
      return newState;
    });
    
    // Show toast notification
    if (newAutoPlayState) {
      setToast('🤖 Autoplay enabled - System will mark cells automatically');
    } else {
      setToast('👤 Manual mode - Click cells to mark them');
    }
    setIsToast(true);
  }, [autoPlay, gameState.hasSufficientBalance, setToast, setIsToast]);

  // Effect to handle autoplay when called numbers change
  useEffect(() => {
    if (!autoPlay || !selectBoard || isBingo || isDisqualified || !gameState.hasSufficientBalance) return;
    
    // Auto-mark cells when called numbers are received
    const calledNumbersArray = calledNumbers.map(num => ({ number: num }));
    const newSelectedCell = new Set(selectedCell);
    let markedCount = 0;
    
    // Mark cells that match called numbers
    selectBoard.forEach(row => {
      row.forEach(cellNumber => {
        if (cellNumber !== '*' && calledNumbers.includes(cellNumber) && !newSelectedCell.has(cellNumber)) {
          newSelectedCell.add(cellNumber);
          markedCount++;
        }
      });
    });
    
    // Update state if there are new marked cells
    if (markedCount > 0) {
      updateGameState({ selectedCell: newSelectedCell });
      setToast(`🤖 Autoplay marked ${markedCount} number(s)`);
      setIsToast(true);
    }
    
    // Check for bingo automatically
    const markedCard = selectBoard.map(row => 
      row.map(cellNumber => ({
        number: cellNumber,
        marked: cellNumber === '*' || newSelectedCell.has(cellNumber)
      }))
    );
    
    // Check if bingo is achieved
    if (hasBingo(markedCard)) {
      console.log('Auto-bingo detected!');
      setToast('🎉 Autoplay detected BINGO!');
      setIsToast(true);
      handleBingo(selectBoard, selectedNumber);
    }
  }, [calledNumbers, autoPlay, selectBoard, selectedCell, isBingo, isDisqualified, selectedNumber, handleBingo, updateGameState, setToast, setIsToast, gameState.hasSufficientBalance]);

  // Deposit reminder effect for users with insufficient balance
  useEffect(() => {
    if (gameState.hasSufficientBalance || depositReminderDismissed) return;
    
    // Show reminder after 30 seconds, then every 30 seconds
    const initialTimer = setTimeout(() => {
      setGameState(prev => ({ ...prev, showDepositReminder: true }));
    }, 30000); // 30 seconds
    
    const intervalTimer = setInterval(() => {
      setGameState(prev => ({ ...prev, showDepositReminder: true }));
    }, 30000); // 30 seconds
    
    return () => {
      clearTimeout(initialTimer);
      clearInterval(intervalTimer);
    };
  }, [gameState.hasSufficientBalance, depositReminderDismissed]);

  // Winner countdown effect
  useEffect(() => {
    if (!isBingo) return;

    const countdownInterval = setInterval(() => {
      updateGameState(prevState => {
        const newCountdown = prevState.winnerCountdown - 1;
        if (newCountdown <= 0) {
          navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);
          window.location.reload();
          return prevState;
        }
        return { winnerCountdown: newCountdown };
      });
    }, 1000);

    return () => clearInterval(countdownInterval);
  }, [isBingo, updateGameState, navigate, playerId, roomId, playerName]);

  return (
    <div className="bingo-game-container">
      <Toaster />

      {/* Watch Mode and Auto-play Indicators */}
      {isWatchMode && (
        <div className="watch-mode-indicator">
          <div className="watch-mode-badge">
            👁️ Watch Mode
          </div>
          <div className="watch-mode-text">
            You're observing the current game
          </div>
        </div>
      )}
      
      {isAutoPlayDisabled && !isWatchMode && (
        <div className="auto-play-disabled-indicator">
          <div className="auto-play-disabled-badge">
            ⚠️ Auto-play Disabled
          </div>
          <div className="auto-play-disabled-text">
            Select your cards manually
          </div>
        </div>
      )}

      {isBingo && (
        <div className="bingo-winner-overlay">
          {/* Liyu Logo Rain Animation */}
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          <div className="liyu-logo-rain">🎯</div>
          
          <div className="bingo-winner-card">
          <div className="winner-summary">
                <span className="summary-text">
                  {winnerPlayerName === playerName ? (
                    <>🎊 Congratulations! You won with Card #{winnerCardNumber} 🎊</>
                  ) : (
                    <>🏆 {winnerPlayerName} won with Card #{winnerCardNumber} 🏆</>
                  )}
                </span>
              </div>
            
            {/* Content Area */}
            <div className="winner-content">
              {/* Winner Information */}
             
             
              {/* Winning Card Display */}
              <div className="winning-card-section">
                {renderWinningCard(winningCard)}
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="winner-actions">
          
              <button className="close-winner-button" onClick={handleCloseWinner}>
                <span className="button-icon">✨</span>
                <span className="button-text">{t('game.continuePlaying')}</span>
                <span className="button-icon">✨</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Deposit Reminder Popup */}
      {showDepositReminder && !gameState.hasSufficientBalance && (
        <div className="deposit-reminder-overlay">
          <div className="deposit-reminder-card">
            {/* Close Button */}
            <button className="deposit-close-button" onClick={handleCloseDepositReminder}>
              <span className="close-icon">×</span>
            </button>
            
            {/* Header */}
            <div className="deposit-reminder-header">
              <div className="deposit-icon">💰</div>
              <h2 className="deposit-title">{t('deposit.boostYourGame')}</h2>
            </div>
            
            {/* Content */}
            <div className="deposit-reminder-content">
              <p className="deposit-message">
                🎮 {t('deposit.limitedFeaturesMessage')}
              </p>
              <p className="deposit-benefits">
                ✨ <strong>{t('deposit.depositNowToUnlock')}</strong><br/>
                🤖 {t('deposit.autoplayFunctionality')}<br/>
                🎯 {t('deposit.bingoCallingAbility')}<br/>
                🏆 {t('deposit.fullGameExperience')}
              </p>
              
              <div className="deposit-amounts">
                <div className="amount-option">💎 50 {t('currency.birr')}</div>
                <div className="amount-option">💎 100 {t('currency.birr')}</div>
                <div className="amount-option">💎 200 {t('currency.birr')}</div>
                <div className="amount-option">💎 500 {t('currency.birr')}</div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="deposit-reminder-actions">
              <button className="deposit-now-button" onClick={handleDepositNow}>
                <span className="button-icon">💳</span>
                <span className="button-text">{t('deposit.depositNow')}</span>
                <span className="button-icon">💳</span>
              </button>
              <button className="dismiss-button" onClick={handleDismissDepositReminder}>
                <span className="button-text">{t('deposit.maybeLater')}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top Stats Bar */}
      <div className="top-stats-bar">
        <div className="stat-item purple">{t('game.bet')} {roomId}ης</div>
        <div className="stat-item blue">{t('game.players')} {displayedTotalPlayers}</div>
        <div className="stat-item green">{t('game.prize')} {displayedWinAmount.toFixed(0)}ης</div>
        <div className="stat-item light-green">{t('game.called')} {totalCalledNumbers}/75</div>
        
        <div className="stat-item dark-purple language-switcher-container">
          <LanguageSelector />
        </div>
      </div>

      {/* Main Game Area */}
      <div className="main-game-area">
        {/* Left Side - Main Bingo Board */}
        <div className="main-bingo-board">
          {/* BINGO Header */}
          <div className="bingo-header">
            <div className="bingo-letter red">B</div>
            <div className="bingo-letter green">I</div>
            <div className="bingo-letter yellow">N</div>
            <div className="bingo-letter blue">G</div>
            <div className="bingo-letter purple">O</div>
          </div>

          {/* Numbers Grid */}
          <div className="numbers-grid">
            {/* B Column */}
            <div className="number-column">
            {Array.from({ length: 15 }, (_, i) => {
                const number = i + 1;
                const isCalled = calledNumbers?.includes(number);
              return (
                <div 
                    key={number} 
                    className={`number-cell ${isCalled ? 'called' : ''}`}
                    id={`B${number}`}
                  >
                    {number}
                </div>
              );
            })}
          </div>

            {/* I Column */}
            <div className="number-column">
              {Array.from({ length: 15 }, (_, i) => {
                const number = i + 16;
                const isCalled = calledNumbers?.includes(number);
                return (
                  <div 
                    key={number} 
                    className={`number-cell ${isCalled ? 'called' : ''}`}
                    id={`I${number}`}
                  >
                    {number}
              </div>
                );
              })}
        </div>
    
            {/* N Column */}
            <div className="number-column">
              {Array.from({ length: 15 }, (_, i) => {
                const number = i + 31;
                const isCalled = calledNumbers?.includes(number);
                return (
                  <div 
                    key={number} 
                    className={`number-cell ${isCalled ? 'called' : ''}`}
                    id={`N${number}`}
                  >
                    {number}
                  </div>
                );
              })}
                    </div>

            {/* G Column */}
            <div className="number-column">
              {Array.from({ length: 15 }, (_, i) => {
                const number = i + 46;
                const isCalled = calledNumbers?.includes(number);
                return (
                  <div 
                    key={number} 
                    className={`number-cell ${isCalled ? 'called' : ''}`}
                    id={`G${number}`}
                  >
                    {number}
                  </div>
                );
              })}
            </div>

            {/* O Column */}
            <div className="number-column">
              {Array.from({ length: 15 }, (_, i) => {
                const number = i + 61;
                const isCalled = calledNumbers?.includes(number);
                return (
                  <div 
                    key={number} 
                    className={`number-cell ${isCalled ? 'called' : ''}`}
                    id={`O${number}`}
                  >
                    {number}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Side - Game Controls and Player Card */}
        <div className="game-controls-section">
          {/* Control Buttons */}
          <div className="control-buttons">
            <button 
              className={`control-btn ${autoPlay ? 'active' : ''} ${!gameState.hasSufficientBalance ? 'disabled' : ''}`}
              onClick={() => {
                console.log('Button clicked!');
                toggleAutoPlay();
              }}
              disabled={!gameState.hasSufficientBalance}
              title={
                !gameState.hasSufficientBalance ? '💰 Autoplay disabled - Insufficient balance' :
                autoPlay ? t('game.autoplayOnTooltip') : t('game.autoplayOffTooltip')
              }
            >
              <FontAwesomeIcon icon={faCog} />
              {autoPlay ? t('game.autoPlayOn') : t('game.autoPlayOff')}
            </button>
            <button 
              className={`control-btn ${isMuted ? 'active' : ''}`}
              onClick={toggleMute}
            >
              <FontAwesomeIcon icon={isMuted ? faVolumeMute : faVolumeUp} />
              {isMuted ? t('game.unmute') : t('game.mute')}
            </button>
              </div>

          {/* Bonus and Countdown / Recent Balls */}
          {gameStatus === 'in-progress' ? (
            <div className="recent-balls-container">
              <div className="recent-balls-label">{t('game.recentBalls')}</div>
              <div className="recent-balls-display">
                {(() => {
                  const recentBalls = calledNumbers.slice(-3);
                  const emptySlots = 3 - recentBalls.length;
                  
                  return [
                    // Show recent balls
                    ...recentBalls.map((number, index) => {
                      // Convert number to BINGO format (B-1, I-16, etc.)
                      let letter = '';
                      let displayNumber = number;
                      if (number >= 1 && number <= 15) {
                        letter = 'B';
                        displayNumber = number;
                      } else if (number >= 16 && number <= 30) {
                        letter = 'I';
                        displayNumber = number;
                      } else if (number >= 31 && number <= 45) {
                        letter = 'N';
                        displayNumber = number;
                      } else if (number >= 46 && number <= 60) {
                        letter = 'G';
                        displayNumber = number;
                      } else if (number >= 61 && number <= 75) {
                        letter = 'O';
                        displayNumber = number;
                      }
                      
                      return (
                        <div key={`ball-${index}`} className="recent-ball">
                          <span className="recent-ball-letter">{letter}</span>
                          <span className="recent-ball-number">{displayNumber}</span>
                        </div>
                      );
                    }),
                    // Show empty slots
                    ...Array.from({ length: emptySlots }, (_, index) => (
                      <div key={`empty-${index}`} className="recent-ball empty">
                        <span className="recent-ball-letter">-</span>
                        <span className="recent-ball-number">-</span>
                      </div>
                    ))
                  ];
                })()}
              </div>
            </div>
          ) : (
            <div className="bonus-countdown">
              <div className="bonus-indicator">
                <span className="star">⭐</span>
                {t('game.bonusOn')}
              </div>
              <div className="countdown-display">
                <span className="countdown-label">{t('game.countdown')}</span>
                <span className={`countdown-timer ${gameStatus === 'in-progress' ? 'active' : ''}`}>
                  {gameCountdown || countDown || 0} : 01
                </span>
              </div>
            </div>
          )}

          {/* Ball Display */}
          <div className="ball-display-container">
            <div className="ball-display">
              {lastBall ? (
                <div className="ball-number">{lastBall.combined}</div>
              ) : (
                <div className="ball-placeholder"></div>
              )}
            </div>
          </div>
    
          {/* Player Card */}
      {selectedNumber && (
            <div className="player-card-section">
              <div className="card-title">Card Number {selectedNumber}</div>
              
              {/* BINGO Header */}
              <div className="card-bingo-header">
                <div className="card-letter red">B</div>
                <div className="card-letter green">I</div>
                <div className="card-letter yellow">N</div>
                <div className="card-letter blue">G</div>
                <div className="card-letter purple">O</div>
              </div>

             
              <div className="player-card-grid">
                {selectBoard && selectBoard.map((row, rowIndex) => {
                  console.log('Rendering row:', rowIndex, 'with data:', row);
                  return (
                    <div key={rowIndex} className="card-row">
                      {row.map((num, colIndex) => {
                        console.log('Rendering cell:', colIndex, 'with number:', num, 'isMarked:', selectedCell.has(num));
                        return (
                          <div 
                            key={colIndex} 
                            className={`card-cell ${num === '*' ? 'free-space' : ''} ${selectedCell.has(num) ? 'marked' : ''}`}
                            onClick={() => handleCellClick(num)}
                          >
                            {num === '*' ? 'F' : num}
                          </div>
                        );
                      })}
          </div>
                  );
                })}
          </div>
          
              {/* Bingo Button */}
              <button 
                className={`bingo-button ${(firstBoardLost || isDisqualified || !selectedNumber || !gameState.hasSufficientBalance) ? 'disabled' : ''}`}
                onClick={() => {
                  console.log('Bingo button clicked!');
                  console.log('Current state:', { 
                    firstBoardLost, 
                    isDisqualified, 
                    selectedNumber, 
                    selectBoard,
                    isBingo,
                    playerId,
                    gameId,
                    hasSufficientBalance: gameState.hasSufficientBalance
                  });
                  handleBingo(selectBoard, selectedNumber);
                }}
                disabled={firstBoardLost || isDisqualified || !selectedNumber || !gameState.hasSufficientBalance}
                title={
                  firstBoardLost ? t('game.boardLost') :
                  isDisqualified ? t('game.disqualified') :
                  !selectedNumber ? t('game.noCardSelected') :
                  !gameState.hasSufficientBalance ? '💰 Insufficient balance - Deposit to enable bingo' :
                  t('game.callBingo')
                }
              >
                {t('game.bingo')}
              </button>
              
           
            </div>

            
          )}

             {/* Bottom Action Buttons */}
             <div className="bottom-actions">
                <button className="action-btn leave-btn" onClick={handleLeaveGame}>
                  <FontAwesomeIcon icon={faSignOutAlt} />
                  {t('game.leaveGame')}
                </button>
                <button className="action-btn refresh-btn" onClick={handleRefresh}>
                  <FontAwesomeIcon icon={faSync} />
                  {t('game.refresh')}
                </button>
              </div>
        </div>

        
        
      </div>
    </div>
  );
};

export default PlayingBoard;