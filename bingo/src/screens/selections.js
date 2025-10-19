import React, { useState, useEffect, useContext, useCallback } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faBars, faTimes, faGamepad, faUser, faHistory, faUsers } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import Toaster from '../components/Toaster';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import checkPlayerBalance from '../api';
import axios from 'axios';
import { generateFixedCard } from '../helpers/fixedBingoCards';
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [totalWinAmount, setTotalWinAmount] = useState(0);
  const [isBingo, setIsBingo] = useState(false);
  const [winnerCardNumber, setWinnerCardNumber] = useState(null);
  const [winnerPlayerName, setWinnerPlayerName] = useState(null);
  const [winningCard, setWinningCard] = useState(null);
  const [isSocketConnected, setIsSocketConnected] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const cardsPerPage = 100;

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
        }
        // Countdown logic removed - navigation now happens immediately on card selection
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

  // Countdown redirect logic removed - navigation now happens immediately on card selection

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
    
    if (isPicked) {
      setToast(`Card ${number} is already selected by another player`);
      setIsToast(true);
      return;
    }
    
    // Check balance before proceeding
    try {
      const apiUrl = config.API_BASE_URL;
      const response = await axios.get(`${apiUrl}wallet/player/${parseInt(playerId)}`);
      const currentBalance = response.data.total_balance;
      
      if (currentBalance < roomId && !isSelected) {
        setToast('Insufficient balance to select this card');
        setIsToast(true);
        return;
      }
      
      // Update balance state
      setBalance(currentBalance);
      
    } catch (error) {
      console.error('Error checking balance:', error);
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
      
      setToast(`Card ${number} unselected. Left the game.`);
      setIsToast(true);
    } else {
      // Select and immediately navigate to main screen
      setChoosenNumbers([number]);
      setSelectedNumber(number);
      
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
      
      setToast(`Card ${number} selected! Redirecting to game...`);
      setIsToast(true);
      
      // Immediately navigate to main screen after a short delay
      setTimeout(() => {
        const queryParams = new URLSearchParams({
          playerId: playerId,
          betAmount: roomId,
          playerName: playerName,
          selectedNumber: number,
          gameId: gameId || 'default'
        });
        
        navigate(`/play?${queryParams.toString()}`);
      }, 1000); // Small delay to show the toast message
    }
  }, [isLoading, isSocketConnected, choosenNumbers, pickedNumbers, balance, roomId, playerId, gameId, socket, setChoosenNumbers, setSelectedNumber, setSelectBoard, setChooseBoards, setToast, setIsToast, playerName, navigate]);

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
              <div className="hamburger-menu" onClick={toggleSidebar}>
                <FontAwesomeIcon icon={faBars} />
            </div>
              <div className="konjo-logo">Liyu</div>
            </div>
            <div className="konjo-title">Liyu Bingo</div>
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

            {/* Selected Card Preview */}
            {selectedNumber && (
              <div className="konjo-card-preview">
                <div className="bingo-card">
                  {/* BINGO Header */}
                  <div className="bingo-header">
                    <div className="bingo-letter">B</div>
                    <div className="bingo-letter">I</div>
                    <div className="bingo-letter">N</div>
                    <div className="bingo-letter">G</div>
                    <div className="bingo-letter">O</div>
                  </div>
                  
                  {/* Card Grid */}
                  <div className="bingo-grid">
                    {selectBoard.map((row, rowIndex) => (
                      <div key={rowIndex} className="bingo-row">
                        {row.map((num, colIndex) => (
                          <div key={colIndex} className={`bingo-cell ${num === '*' ? 'free-space' : ''}`}>
                            {num === '*' ? (
                              <div className="free-space-content">
                                <div className="free-text">FREE</div>
                                <div className="space-text">SPACE</div>
                              </div>
                            ) : (
                              num
                            )}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="card-preview-number">Card #{selectedNumber}</div>
              </div>
            )}

            {/* Countdown removed - navigation happens immediately on card selection */}
                  </div>

          {/* Bottom Message */}
          <div className="konjo-bottom-message">
            Welcome to Liyu Bingo Bot! Choose an option.
          </div>
        </div>
      )}

      {/* Sidebar */}
      {isSidebarOpen && (
        <>
          <div className="sidebar-overlay" onClick={toggleSidebar}></div>
          <div className="sidebar">
            <div className="sidebar-header">
              <div className="sidebar-title">Menu</div>
              <button className="sidebar-close" onClick={toggleSidebar}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
            <div className="sidebar-content">
              <div className="sidebar-menu">
                <div className="sidebar-item" onClick={() => handleNavigation('bingo')}>
                  <FontAwesomeIcon icon={faGamepad} className="sidebar-icon" />
                  <span>Bingo Game</span>
                          </div>
                <div className="sidebar-item" onClick={() => handleNavigation('profile')}>
                  <FontAwesomeIcon icon={faUser} className="sidebar-icon" />
                  <span>Profile</span>
                      </div>
                <div className="sidebar-item" onClick={() => handleNavigation('transactions')}>
                  <FontAwesomeIcon icon={faHistory} className="sidebar-icon" />
                  <span>Transaction History</span>
                  </div>
                <div className="sidebar-item" onClick={() => handleNavigation('invited-users')}>
                  <FontAwesomeIcon icon={faUsers} className="sidebar-icon" />
                  <span>Invited Users</span>
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