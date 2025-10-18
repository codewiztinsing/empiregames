import React, { useState, useEffect, useContext, useCallback } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import Toaster from '../components/Toaster';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import checkPlayerBalance from '../api';
import axios from 'axios';
import config from '../config/api';

const Selections = () => {
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
  const [totalWinAmount, setTotalWinAmount] = useState(0);
  const [isBingo, setIsBingo] = useState(false);
  const [winnerCardNumber, setWinnerCardNumber] = useState(null);
  const [winnerPlayerName, setWinnerPlayerName] = useState(null);
  const [winningCard, setWinningCard] = useState(null);
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

  // Socket listeners
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const urlPlayerId = queryParams.get('playerId');
    const urlRoomId = queryParams.get('betAmount');
    const urlPlayerName = queryParams.get('playerName');
      
    setPlayerId(urlPlayerId);
    setRoomId(urlRoomId);
    setPlayerName(urlPlayerName);
   
    if (urlPlayerId && urlRoomId) {
      socket.emit("playerJoined", { playerId: urlPlayerId, roomId: urlRoomId });
    }

    const handleGameState = (state) => {
      console.log('handleGameState received:', state);
      
      if (state.pickedNumbers !== null && state.pickedNumbers && state.pickedNumbers.numbers) {
        setPickedNumbers(state.pickedNumbers.numbers);
      }
      
      if (state.game_status === "in-progress") {
        if (gameStatus !== "in-progress") {
          setToast("🎮 Game Started! Good luck!");
          setIsToast(true);
        }
        setGameStatus("in-progress");
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
      }
     
      if (state.game_status !== "in-progress") {
        setPlayersLength(state.total_players);
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
        } else if (state.count_down === 0 && selectedNumber) {
          // Redirect to play screen when countdown reaches 0
          setToast("🚀 Game starting! Redirecting to play screen...");
          setIsToast(true);
          
          // Build query parameters
          const queryParams = new URLSearchParams({
            playerId: playerId,
            betAmount: roomId,
            playerName: playerName,
            selectedNumber: selectedNumber,
            gameId: gameId || 'default'
          });
          
          // Redirect to play screen
          setTimeout(() => {
            navigate(`/play?${queryParams.toString()}`);
          }, 1000); // Small delay to show the toast message
        }
      }
    };

    const handlePickedNumbers = (data) => {
      console.log('handlePickedNumbers received:', data);
      if (data.numbers) {
        setPickedNumbers(data.numbers);
      }
    };

    const handleGameStatus = (status) => {
      console.log('Game status changed:', status);
      setGameStatus(status);
    };

    const handleBingoWinner = (data) => {
      console.log('Bingo winner:', data);
      setWinnerCardNumber(data.winnerCardNumber);
      setWinnerPlayerName(data.winnerPlayerName);
      setWinningCard(data.winningCard);
      setIsBingo(true);
    };

    const handleRejoinSuccess = (data) => {
      console.log('Rejoin success:', data);
      setSelectedNumber(data.selectedNumber);
      setSelectBoard(data.selectBoard);
      setChoosenNumbers([data.selectedNumber]);
    };

    const handleRejoinError = (error) => {
      console.error('Rejoin error:', error);
      setToast(error.message || 'Failed to rejoin game');
      setIsToast(true);
    };

    const handleAllPlayerSelections = (data) => {
      console.log('All player selections:', data);
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
  }, [socket, playerId, roomId, playerName, setPlayerId, setPlayerName, setRoomId, gameStatus, countDown, setToast, setIsToast, setPlayersLength, setCountDown, navigate]);

  // Fetch balance when playerId is available
  useEffect(() => {
    if (playerId) {
      const fetchBalance = async () => {
        const apiUrl = config.API_BASE_URL;
        try {
          const response = await axios.get(`${apiUrl}wallet/player/${parseInt(playerId)}`);
          setBalance(response.data.total_balance);
          setLoading(false);
        } catch (error) {
          console.error('Error fetching balance:', error);
          setLoading(false);
        }
      };
      fetchBalance();
    }
  }, [playerId]);

  // Handle countdown redirect
  useEffect(() => {
    if (countDown === 0 && selectedNumber && gameStatus === "countdown") {
      console.log('Countdown reached 0, redirecting to play screen');
      
      // Build query parameters
      const queryParams = new URLSearchParams({
        playerId: playerId,
        betAmount: roomId,
        playerName: playerName,
        selectedNumber: selectedNumber,
        gameId: gameId || 'default'
      });
      
      // Redirect to play screen
      setTimeout(() => {
        navigate(`/play?${queryParams.toString()}`);
      }, 500); // Small delay to ensure state is updated
    }
  }, [countDown, selectedNumber, gameStatus, playerId, roomId, playerName, gameId, navigate]);

  // Handle number click
  const handleNumberClick = useCallback((number) => {
    if (isLoading || !isSocketConnected) return;

    const isSelected = choosenNumbers.includes(number);
    const isPicked = pickedNumbers.includes(number);
    
    if (isPicked) {
      setToast(`Card ${number} is already selected by another player`);
      setIsToast(true);
      return;
    }

    if (balance < roomId && !isSelected) {
      setToast('Insufficient balance to select this card');
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
      
      setToast(`Card ${number} unselected. Left the game.`);
      setIsToast(true);
    } else {
      // Select
      setChoosenNumbers([number]);
      setSelectedNumber(number);
      
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
      
      setToast(`Card ${number} selected! Joining game...`);
      setIsToast(true);
    }
  }, [isLoading, isSocketConnected, choosenNumbers, pickedNumbers, balance, roomId, playerId, gameId, socket, setChoosenNumbers, setSelectedNumber, setSelectBoard, setChooseBoards, setToast, setIsToast]);

  return (
    <>
      {isToast && <Toaster message={toast} />}
      {loading && <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading...</div>
      </div>}

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
              <div className="hamburger-menu">☰</div>
              <div className="konjo-logo">KONJO</div>
            </div>
            <div className="konjo-title">KONJO Bingo</div>
            <div className="konjo-header-right">
              <div className="balance-button">
                <span className="balance-amount">{parseInt(balance)} ETB</span>
                <div className="user-icon">👤</div>
              </div>
            </div>
          </div>

          {/* Sub-header */}
          <div className="konjo-sub-header">
            <div className="back-button">
              <FontAwesomeIcon icon={faArrowLeft} />
            </div>
            <div className="info-buttons">
              <div className="info-button">Wallet {parseInt(balance)} ብር</div>
              <div className="info-button">Stake {roomId} ብር</div>
              <div className="info-button">⭐ Bonus</div>
            </div>
            <div className="action-button">ምረጥ</div>
          </div>

          {/* Main Content */}
          <div className="konjo-main-content">
            {/* Waiting Message */}
            <div className="waiting-message">
              Waiting for players...
            </div>

            {/* Number Grid 1-100 */}
            <div className="konjo-number-grid">
              {Array.from({ length: 100 }, (_, i) => {
                const number = i + 1;
                const isSelected = choosenNumbers.includes(number);
                const isPicked = pickedNumbers.includes(number);
                const isDisabled = isPicked || !isSocketConnected || (balance < roomId && !isSelected);

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

            {/* Selected Card Preview */}
            {selectedNumber && (
              <div className="konjo-card-preview">
                <div className="card-preview-title">Your Selected Card</div>
                <div className="card-preview-grid">
                  {selectBoard.map((row, rowIndex) => (
                    <div key={rowIndex} className="card-preview-row">
                      {row.map((num, colIndex) => (
                        <div key={colIndex} className={`card-preview-cell ${num === '*' ? 'free-space' : ''}`}>
                          {num === '*' ? 'FREE' : num}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
                <div className="card-preview-number">Card #{selectedNumber}</div>
              </div>
            )}

            {/* Countdown */}
            {gameStatus === "waiting" && countDown > 0 && (
              <div className="konjo-countdown">
                Game starts in: {countDown}
              </div>
            )}
          </div>

          {/* Bottom Message */}
          <div className="konjo-bottom-message">
            Welcome to Konjo Bingo Bot! Choose an option.
          </div>
        </div>
      )}
    </>
  );
};

export default Selections;