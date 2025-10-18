import React, { useState, useContext, useEffect, useCallback, useMemo } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog, faVolumeMute, faVolumeUp, faSignOutAlt, faSync } from '@fortawesome/free-solid-svg-icons';
import { generateFixedCard } from '../helpers/fixedBingoCards';
import { hasBingo, checkBingoPatterns, markCardNumber } from '../helpers/fixedBingoCards';

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
    winAmount: 0,
    totalWinAmount: 0,
    totalPlayers: 0,
    recentCalledNumbers: ['*', '*', '*'],
    winnerCountdown: 5,
    isMuted: false,
    autoPlay: false
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
    autoPlay
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
    const urlRoomId = queryParams.get('betAmount');
    const urlPlayerName = queryParams.get('playerName');
    const urlSelectedNumber = queryParams.get('selectedNumber');
    
    if (urlPlayerId) setPlayerId(urlPlayerId);
    if (urlRoomId) setRoomId(parseInt(urlRoomId));
    if (urlPlayerName && urlPlayerName !== 'null') setPlayerName(urlPlayerName);
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
        updateGameState({ calledNumbers: calledNumbersArray });
        
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
          calledNumbers: [...prevState.calledNumbers, parseInt(calledNumber)]
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

  // Socket event bindings
  useEffect(() => {
    if (!socket) return;

    socket.on('gameState', handleGameState);
    socket.on('bingoWinner', handleBingoWinner);
    socket.on('falseBingo', handleFalseBingo);
    socket.on('disqualified', handleDisqualified);

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('bingoWinner', handleBingoWinner);
      socket.off('falseBingo', handleFalseBingo);
      socket.off('disqualified', handleDisqualified);
    };
  }, [socket, handleGameState, handleBingoWinner, handleFalseBingo, handleDisqualified]);

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
      
      if (!board || !cardNumber || isBingo || isDisqualified) {
        console.log('Bingo call blocked:', { 
          hasBoard: !!board, 
          hasCardNumber: !!cardNumber, 
          isBingo, 
          isDisqualified 
        });
        return;
      }
      
      console.log('Emitting bingo event to server...');
      socket.emit('bingo', {
        playerId,
        gameId,
        boardNumber: cardNumber,
        board,
        playerName
      });
      
      console.log('Bingo event emitted successfully');
    } catch (error) {
      console.error('Error handling bingo:', error);
    }
  }, [socket, playerId, gameId, isBingo, isDisqualified]);

  const handleCloseWinner = useCallback(() => {
    try {
      updateGameState({
        isBingo: false,
        winnerCardNumber: null,
        winnerPlayerName: null,
        winningCard: null
      });
    } catch (error) {
      console.error('Error closing winner:', error);
    }
  }, [updateGameState]);

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
  }, [autoPlay, setToast, setIsToast]);

  // Effect to handle autoplay when called numbers change
  useEffect(() => {
    if (!autoPlay || !selectBoard || isBingo || isDisqualified) return;
    
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
  }, [calledNumbers, autoPlay, selectBoard, selectedCell, isBingo, isDisqualified, selectedNumber, handleBingo, updateGameState, setToast, setIsToast]);

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

      {isBingo && (
        <div className="bingo-winner-overlay">
    <div className="bingo-winner-card">
      {/* Animated Countdown */}
      <div className="winner-countdown">
        <div className="countdown-icon">⏰</div>
        <p>Returning to home in: <span className="countdown-number">{winnerCountdown}</span> seconds</p>
      </div>
      
      {/* Winner Header with Celebration */}
      <div className="winner-card-header">
        <div className="celebration-icons">
          <span className="celebration-icon">🎉</span>
          <span className="celebration-icon">🏆</span>
          <span className="celebration-icon">🎊</span>
        </div>
        <p className='winner-card-header-text'>🎯 BINGO WINNER! 🎯</p>
        <div className="winner-divider"></div>
      </div>
      
      {/* Winner Information */}
      <div className="winner-info">
        <div className="winner-card-number">
          <span className="info-label">🏷️ Winning Card Number:</span>
          <span className="info-value">{winnerCardNumber}</span>
        </div>
        <div className="winner-player-name">
          <span className="info-label">👤 Winner Name:</span>
          <span className="info-value">{winnerPlayerName}</span>
        </div>
      </div>
     
      {/* Winning Card Display */}
      <div className="winning-card-section">
        <h3 className="winning-card-title">🎲 Winning Bingo Card 🎲</h3>
        <div className="winning-card">
          <div className="winning-card-row">
            {["B", "I", "N", "G", "O"].map((letter, index) => (
              <div key={index} className="winning-card-cell winning-card-header">
                <span className="bingo-letter">{letter}</span>
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
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="winner-actions">
        <div className="winner-summary">
          <span className="summary-text">🎊 Congratulations! You won with Card #{winnerCardNumber} 🎊</span>
        </div>
        <button className="close-winner-button" onClick={handleCloseWinner}>
          <span className="button-icon">✨</span>
          <span className="button-text">Continue Playing</span>
          <span className="button-icon">✨</span>
        </button>
      </div>
    </div>
      )}

      {/* Top Stats Bar */}
      <div className="top-stats-bar">
        <div className="stat-item purple">Bet {roomId}ης</div>
        <div className="stat-item blue">Players {displayedTotalPlayers}</div>
        <div className="stat-item green">ደራሽ {displayedWinAmount.toFixed(0)}ης</div>
        <div className="stat-item light-green">የተጠራ {totalCalledNumbers}/75</div>
        <div className="stat-item dark-purple">አማርኛ</div>
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
              className={`control-btn ${autoPlay ? 'active' : ''}`}
              onClick={() => {
                console.log('Button clicked!');
                toggleAutoPlay();
              }}
              title={autoPlay ? 'Autoplay is ON - System will mark cells automatically' : 'Autoplay is OFF - Click to enable automatic marking'}
            >
              <FontAwesomeIcon icon={faCog} />
              {autoPlay ? 'Auto Play ON' : 'Auto Play OFF'}
            </button>
            <button 
              className={`control-btn ${isMuted ? 'active' : ''}`}
              onClick={toggleMute}
            >
              <FontAwesomeIcon icon={isMuted ? faVolumeMute : faVolumeUp} />
              {isMuted ? 'un-mute' : 'mute'}
            </button>
              </div>

          {/* Bonus and Countdown */}
          <div className="bonus-countdown">
            <div className="bonus-indicator">
              <span className="star">⭐</span>
              Bonus On
            </div>
            <div className="countdown-display">
              <span className="countdown-label">Count Down</span>
              <span className="countdown-timer">{countDown || 0} : 01</span>
            </div>
          </div>

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
                className="bingo-button"
                onClick={() => {
                  console.log('Bingo button clicked!');
                  handleBingo(selectBoard, selectedNumber);
                }}
                disabled={firstBoardLost || isDisqualified || !selectedNumber}
              >
                Bingo
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Action Buttons */}
      <div className="bottom-actions">
        <button className="action-btn leave-btn" onClick={handleLeaveGame}>
          <FontAwesomeIcon icon={faSignOutAlt} />
          Leave Game
        </button>
        <button className="action-btn refresh-btn" onClick={handleRefresh}>
          <FontAwesomeIcon icon={faSync} />
          Refresh
        </button>
      </div>
    </div>
  );
};

export default PlayingBoard;