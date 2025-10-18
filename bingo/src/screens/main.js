import React, { useState, useContext, useEffect, useCallback, useMemo } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { SocketContext } from '../contexts/socket';
import { useNavigate } from 'react-router-dom';
import './main.css';
import { BingoContext } from '../contexts/bingoContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCog, faVolumeMute, faVolumeUp, faSignOutAlt, faSync } from '@fortawesome/free-solid-svg-icons';

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
        // Generate card data
        const generateCard = (cardNumber) => {
          const card = [];
          const ranges = [
            { min: 1, max: 15 },   // B
            { min: 16, max: 30 },  // I
            { min: 31, max: 45 },  // N
            { min: 46, max: 60 },  // G
            { min: 61, max: 75 }   // O
          ];
          
          for (let col = 0; col < 5; col++) {
            const column = [];
            const usedNumbers = new Set();
            
            for (let row = 0; row < 5; row++) {
              if (col === 2 && row === 2) {
                column.push('*'); // Free space
              } else {
                let num;
                do {
                  num = Math.floor(Math.random() * (ranges[col].max - ranges[col].min + 1)) + ranges[col].min;
                } while (usedNumbers.has(num));
                usedNumbers.add(num);
                column.push(num);
              }
            }
            card.push(column);
          }
          return card;
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

  // Socket event bindings
  useEffect(() => {
    if (!socket) return;

    socket.on('gameState', handleGameState);
    socket.on('bingoWinner', handleBingoWinner);

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('bingoWinner', handleBingoWinner);
    };
  }, [socket, handleGameState, handleBingoWinner]);

  const handleCellClick = useCallback((number) => {
    try {
      if (number === '*' || isBingo || isDisqualified) return;
      
      updateGameState(prevState => {
        const newSelectedCell = new Set(prevState.selectedCell);
        if (newSelectedCell.has(number)) {
          newSelectedCell.delete(number);
        } else {
          newSelectedCell.add(number);
        }
        return { selectedCell: newSelectedCell };
      });
    } catch (error) {
      console.error('Error handling cell click:', error);
    }
  }, [isBingo, isDisqualified, updateGameState]);

  const handleBingo = useCallback((board, cardNumber) => {
    try {
      if (!board || !cardNumber || isBingo || isDisqualified) return;
      
      socket.emit('bingo', {
        playerId,
        gameId,
        cardNumber,
        board
      });
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
    updateGameState(prevState => ({ autoPlay: !prevState.autoPlay }));
  }, [updateGameState]);

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
            <div className="winner-countdown">
              <p>Returning to home in: {winnerCountdown} seconds</p>
            </div>
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
              <button className="close-winner-button" onClick={handleCloseWinner}>
                <p>Close</p>
              </button>
            </div>
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
              onClick={toggleAutoPlay}
            >
              <FontAwesomeIcon icon={faCog} />
              Play Auto
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

              {/* Player Card Grid */}
              <div className="player-card-grid">
                {selectBoard && selectBoard.map((row, rowIndex) => (
                  <div key={rowIndex} className="card-row">
                    {row.map((num, colIndex) => (
                      <div 
                        key={colIndex} 
                        className={`card-cell ${num === '*' ? 'free-space' : ''} ${selectedCell.has(num) ? 'marked' : ''}`}
                        onClick={() => handleCellClick(num)}
                      >
                        {num === '*' ? 'F' : num}
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              {/* Bingo Button */}
              <button 
                className="bingo-button"
                onClick={() => handleBingo(selectBoard, selectedNumber)}
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