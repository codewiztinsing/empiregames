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
  const [winningCard, setWinningCard] = useState([]);
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [isSocketConnected, setIsSocketConnected] = useState(false);
  const [referralBonus, setReferralBonus] = useState(0);
  const [referralLoading, setReferralLoading] = useState(true);

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 400 }, (_, i) => i + 1);

  

  // Check if cell clicking should be disabled (only for websocket connection)
  const isCellClickDisabled = () => {
    // Only disable if websocket is not connected
    if (!isSocketConnected) {
      return true;
    }
    
    // Don't disable for balance issues - show message instead
    return false;
  };



  // Socket connection state monitoring
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

    // Check initial connection state
    setIsSocketConnected(socket.connected);

    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('connect_error', handleConnectError);
    };
  }, [socket]);

  // Socket listeners with cleanup
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
      
      // Request all player selections
      console.log("📥 Requesting all player selections...");
      socket.emit("getAllPlayerSelections", { 
        playerId: urlPlayerId, 
        roomId: urlRoomId 
      });
      
      // Try to rejoin if there's a previous game in progress
      attemptRejoin(urlPlayerId, urlRoomId, urlPlayerName);
    }
    
    socket.on('gameState', handleGameState);
    socket.on('pickedNumbers', handlePickedNumbers);
    socket.on("gameStatus", handleGameStatus);
    socket.on("bingoWinner", handleBingoWinner);
    socket.on('rejoinSuccess', handleRejoinSuccess);
    socket.on('rejoinError', handleRejoinError);
    socket.on('allPlayerSelections', handleAllPlayerSelections);
    
    // Test if the listener is working
    console.log("🔍 Socket listeners set up. Listening for allPlayerSelections event");
    console.log("🔍 Socket connected:", socket.connected);
    console.log("🔍 Current playerId:", playerId);
    console.log("🔍 Current roomId:", roomId);

    return () => {
      socket.off('gameState', handleGameState);
      socket.off('pickedNumbers', handlePickedNumbers);
      socket.off("gameStatus", handleGameStatus);
      socket.off("bingoWinner", handleBingoWinner);
      socket.off('rejoinSuccess', handleRejoinSuccess);
      socket.off('rejoinError', handleRejoinError);
      socket.off('allPlayerSelections', handleAllPlayerSelections);
    };
  }, [socket]);



  // Attempt to rejoin a previous game
  const attemptRejoin = (playerId, roomId, playerName) => {
    console.log("attemptRejoin",playerId, roomId, playerName)
    socket.emit('rejoinGame', {
      playerId: playerId,
      roomId: roomId,
      playerName: playerName
    });
  };

  // Handle successful rejoin
  const handleRejoinSuccess = (data) => {
    console.log("=== REJOIN SUCCESS DEBUG ===");
    console.log("Rejoin success data:", data);
    console.log("Setting game state...");
    
    setToast('Rejoined your previous game! Redirecting to play...');
    setIsToast(true);
    

    
    // Set the game state from rejoin data
    setGameId(data.gameId);
    setSelectedNumber(data.selectedNumber);
    setSelectBoard(data.boards[0]);
    setChoosenNumbers([data.selectedNumber]);
    setChooseBoards(data.boards);
        // Navigate directly to play screen with current game state
    navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${data.selectedNumber2}`);
  };

  // Handle rejoin error
  const handleRejoinError = (data) => {
    console.log("=== REJOIN ERROR DEBUG ===");
    console.log("Rejoin failed:", data.message);
    console.log("This is normal for new users or expired games");
  };

  // Handle all player selections
  const handleAllPlayerSelections = (data) => { 
    console.log("=== ALL PLAYER SELECTIONS ===");
    console.log("Received all player selections:", data);

    // Get playerId, roomId, and playerName from query params
    const searchParams = new URLSearchParams(window.location.search);
    const playerId = searchParams.get('playerId');
    const roomId = searchParams.get('betAmount');
    const playerName = searchParams.get('playerName');
    const game_status = data.game_status;
    
    console.log("Query params - playerId:", playerId, "roomId:", roomId, "playerName:", playerName);
    console.log("Game status:", game_status);
  
    
    if (data.players && Array.isArray(data.players)) {
      console.log("Total players with selections:", data.players.length);
      
      // Process current player selection
      const currentPlayerSelection = data.players.find(p => p.playerId === playerId);
      console.log("Current player selection found:", currentPlayerSelection);
      
      if(currentPlayerSelection) {
        const selectedNumber = currentPlayerSelection.selectedNumbers[0];
        console.log("Selected number from data:", selectedNumber);
        
        if(selectedNumber && game_status == "in-progress") {
          console.log("✅ Current player has a selection - navigating to play screen");
          console.log("playerId:", playerId);
          console.log("betAmount:", roomId);
          console.log("playerName:", playerName);
          console.log("selectedNumber:", selectedNumber);
          
          // Navigate to play screen with the selected number
          navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
        } else {
          console.log("❌ Current player found but no selected number or game not in progress");
          console.log("selectedNumber:", selectedNumber);
          console.log("game_status:", game_status);
          navigate(`/?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}`);

        }
      } else {
        console.log("❌ Current player not found in selections - staying on selection page");
      }
    } else {
      console.log("No players data received or invalid format");
    }
  };

  // Handle bingo winner timeout
  useEffect(() => {
    if (isBingo) {
      const timer = setTimeout(() => {
        setIsBingo(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [isBingo]);

  // Fetch balance when playerId is available
  useEffect(() => {
    console.log('Balance useEffect triggered, playerId:', playerId);

    if (playerId) {
      const fetchBalance = async () => {
        const apiUrl = config.API_BASE_URL;
        console.log('Fetching balance from:', `${apiUrl}wallet/player/${playerId}`);
        
        try {
          const response = await axios.get(`${apiUrl}wallet/player/${parseInt(playerId)}`);
          console.log('Balance response:', response.data);
          setBalance(response.data.balance);
          
      
          setLoading(false);
        } catch (error) {
          console.error('Error fetching data:', error);
          console.error('Error details:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data,
            playerId: playerId,
            parsedPlayerId: parseInt(playerId),
            url: `${apiUrl}/wallet/player/${parseInt(playerId)}`
          });
          setBalance(0);
          setReferralBonus(0);
          setLoading(false);
        }
      };
      
      fetchBalance();
    } else {
      // If no playerId, still set loading to false after a short delay
      console.log('No playerId available, setting loading to false');
      const timer = setTimeout(() => {
        setLoading(false);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [playerId]);

  // Countdown redirect logic - only navigate when countdown reaches exactly 00
  useEffect(() => {
    console.log("gameStatus",gameStatus)
    if(gameStatus == "in-progress") {
      console.log("allPlayerSelections called")
      socket.on("allPlayerSelections", (data) => {
        console.log("allPlayerSelections called",data)
        const selectedNumber = data.players.find(p => p.playerId === playerId)?.selectedNumbers[0];
        navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
      });
     
    }
    // Navigate when countdown reaches 0 and user has selected a number
    if (countDown === 0 && gameStatus != "waiting") {
      // Navigate to play section when countdown reaches 00
      setToast("Game starting! Redirecting to play section...");
      setIsToast(true);
      navigate(`/play?playerId=${playerId}&betAmount=${roomId}&playerName=${playerName}&selectedNumber=${selectedNumber}`);
    }
    // If countdown is not 0, stay on selection page (no navigation)
  }, [countDown, selectedNumber,gameStatus]);




const handleGlobals = (state) => {
  // Show global countdown and game state for all rooms
  if (state.countDown !== undefined) {
    setCountDown(state.countDown);
  }
  if (state.lastBall && state.lastBall?.number) {
    // handlePlaySound(state.lastBall?.number)
    setCurrentCall(state.lastBall?.number);
    setCalledNumbers(state.calledNumbers);
  }
 
  setTotalPlayers(state.totalPlayers);
  setTotalCalledNumbers(state.totalCalledNumbers);
  setTotalWinAmount(state.totalWinAmount);
}

  const handleBingoWinner = (state) => {
    console.log("bingoWinner",state)
    setIsBingo(true);
    setWinnerCardNumber(state.winnerCardNumber);
    setWinnerPlayerName(state.winnerPlayerName);
    setWinningCard(state.winningCard);
  }

  const handleGameState = (state) => {
    // Show game state for all rooms, prioritizing current room if available
    if (state.pickedNumbers !== null && state.pickedNumbers && state.pickedNumbers.numbers) {
      setPickedNumbers(state.pickedNumbers.numbers);
    }
    if (state.game_status == "in-progress") {
      setGameStatus("in-progress");
    }
    if (state.game_status == "waiting") {
      setGameStatus("waiting");
    }
   
    if (state.game_status != "in-progress") {
      setPlayersLength(state.total_players);
    }
    if (state.count_down !== undefined) {
      setCountDown(state.count_down);
    }
  };

  socket.on('globals', handleGlobals);

  socket.on('activeGames', (state) => {
    if (state?.activeGames?.length > 0) {
      // Show active game status for all rooms
      setGameStatus("in-progress");
    }
  });

  socket.on('gameState', (state) => {

    // Show game state for all rooms
    if (state.pickedNumbers !== null && state.pickedNumbers && state.pickedNumbers.numbers) {
      setPickedNumbers(state.pickedNumbers.numbers);
    }

    if (state.game_status != "in-progress") {
      setPlayersLength(state.total_players);
    }
    if (state.count_down !== undefined) {
      setCountDown(state.count_down);
    }
  });



  // Memoized board generation
  const generateCombination = useCallback(() => {
    const card = [];
    const ranges = [
      [1, 15],    // BfAlexo
      [16, 30],   // I
      [31, 45],   // N
      [46, 60],   // G
      [61, 75],   // O
    ];

    for (let col = 0; col < 5; col++) {
      const nums = [];
      for (let n = ranges[col][0]; n <= ranges[col][1]; n++) {
        nums.push(n);
      }

      for (let row = 0; row < 5; row++) {
        if (!card[row]) card[row] = [];
        if (col === 2 && row === 2) {
          card[row][col] = '*';
        } else {
          const idx = Math.floor(Math.random() * nums.length);
          card[row][col] = nums.splice(idx, 1)[0];
        }
      }
    }
    // return card;
    // Transpose the card array
    const transposedCard = card[0].map((_, colIndex) =>
      card.map(row => row[colIndex])
    );
    return transposedCard;


  }, []);


  const handlePickedNumbers = (state) => {
    // Show picked numbers for all rooms, not just the current one
    setPickedNumbers(state.numbers);
  }



  socket.on('joinError', (error) => {
    setToast(error.message);
    setIsToast(true);
    setJoinError(true);
    return;
  })

  const handleNumberClick = async (number) => {
    // Check if this number is already chosen (for unselecting)
    const isCurrentlyChosen = choosenNumbers.includes(number);
    
    // Check if websocket is connected
    if (!isSocketConnected) {
      setToast("Please wait for connection to be established");
      setIsToast(true);
      return;
    }

    console.log("isCurrentlyChosen",isCurrentlyChosen)
  
    // If number is already chosen, remove it (unselect) - skip balance checks for unselecting
    if (isCurrentlyChosen) {
      console.log("✅ UNSELECTING CARD:", number);
      const index = choosenNumbers.indexOf(number);
    
      if (index > -1) {
        const newNumbers = [...choosenNumbers];
        const newBoards = [...choosenBoards];
        newNumbers.splice(index, 1);
        newBoards.splice(index, 1);
        
        setChoosenNumbers(newNumbers);
        setChooseBoards(newBoards);

        // Reset card after removal
        if (newNumbers.length === 0) {
          // Leave game before resetting selectedNumber
          handleLeaveGame();
          setSelectedNumber(null);
          setSelectBoard([]);
          setToast(`Card ${number} unselected! No cards remaining.`);
        } else {
          // One card remains - update to the first remaining card
          setSelectedNumber(newNumbers[0]);
          setSelectBoard(newBoards[0]);
          setToast(`Card ${number} unselected! Now using Card ${newNumbers[0]}.`);
        }
      } else {
        console.log("❌ ERROR: Could not find index for number:", number);
      }
      setIsToast(true);
      return;
    }
    
    // Balance checks only apply when selecting (not unselecting)
    if (balance === 0) {
      console.log("❌ Balance is zero");
      if (loading) {
        setToast("Please wait while we fetch your balance");
      } else {
        setToast("Your balance is zero. Please deposit to play");
      }
      setIsToast(true);
      return;
    }
    
    if (balance < parseInt(roomId)) {
      console.log("❌ Insufficient balance");
      setToast(`Insufficient balance. You need ${parseInt(roomId)} ETB but have ${balance} ETB. Please deposit more to play.`);
      setIsToast(true);
      return;
    }
    
    if (pickedNumbers && pickedNumbers.length > 0 && pickedNumbers.includes(number)) {
      console.log("❌ Number already picked by another player");
      setToast(`Card number ${number} is already selected by another player. Please choose a different number.`);
      setIsToast(true);
      return;
    }
   
    // If user already has a card selected, replace it with new one
    if (choosenNumbers.length >= 1) {
      // Leave current game first (but don't reset selection)
      handleLeaveGame(true);
      // Generate new board for the new number
      const newBoard = generateCombination();
      
      // Replace the existing selection
      setChoosenNumbers([number]);
      setChooseBoards([newBoard]);
      setSelectedNumber(number);
      setSelectBoard(newBoard);
      
      // Join game with new card
      await handleJoinGame(number, newBoard);
      
      // Show toast for card switch
      setToast(`Switched to Card ${number}! Waiting for countdown...`);
      setIsToast(true);
      return;
    }
  
    // Add new number and generate new board (for first selection)
    const newNumbers = [...choosenNumbers, number];
    const newBoard = generateCombination();
    const newBoards = [...choosenBoards, newBoard];
  
    setChoosenNumbers(newNumbers);
    setChooseBoards(newBoards);
  
    // Set the single card
    setSelectedNumber(newNumbers[0]);
    setSelectBoard(newBoards[0]);
    
    // Join game immediately with the selected number
    await handleJoinGame(newNumbers[0], newBoards[0]);
  };

  // Handle double click to unselect and leave game
  const handleNumberDoubleClick = (number) => {
    if (choosenNumbers.includes(number)) {
      // Unselect the card and leave game
      const index = choosenNumbers.indexOf(number);
      if (index > -1) {
        // Leave game before resetting states
        handleLeaveGame();
        
        const newNumbers = [...choosenNumbers];
        const newBoards = [...choosenBoards];
        newNumbers.splice(index, 1);
        newBoards.splice(index, 1);

        setChoosenNumbers(newNumbers);
        setChooseBoards(newBoards);
        setSelectedNumber(null);
        setSelectBoard([]);
        
        setToast(`Card ${number} unselected! Left the game.`);
        setIsToast(true);
      }
    }
  };

  // Join game function - NEVER navigates, only joins and waits for countdown
  const handleJoinGame = async (selectedNum = selectedNumber, selectBoardData = selectBoard) => {
    console.log("handleJoinGame", "selectedNum:", selectedNum, "selectedNumber:", selectedNumber)
    if (!selectedNum || !playerId || !gameId) {
      console.log("Missing required data:", { selectedNum, playerId, gameId });
      return;
    }
    
    if (gameStatus === "in-progress") {
      console.log("Game is already in progress")
      setToast("Game is already in progress");
      setIsToast(true);
      return;
    }

    if (balance < parseInt(roomId) || balance === 0) {
      console.log("Insufficient balance")
      setToast("Insufficient balance");
      setIsToast(true);
      return;
    }

    try {
      console.log("Joining game...")
      setToast("Joining game...");
      setIsToast(true);

      const data = {
        playerId,
        gameId,
        selectedNumber: selectedNum,
        roomId,
        selectBoard: selectBoardData,
        numberOfBoards: choosenBoards.length 
      }
      console.log("data",data)
      
      socket.emit('joinGame', data);

      setToast(`Card ${selectedNum} selected! Waiting for countdown to reach 00...`);
      setIsToast(true);
    } catch (error) {
      console.error('Error joining game:', error);
      setToast("Error joining game");
      setIsToast(true);
    }
  };

  // Leave game function
  const handleLeaveGame = (isSwitchingCard = false) => {
    if (selectedNumber) {
      socket.emit('leave', { 
        playerId, 
        roomId, 
        selectedNumber, 
        reason: isSwitchingCard ? 'switching_card' : 'user_left' 
      });
      
      // Only reset selection if not switching cards
      if (!isSwitchingCard) {
        setChoosenNumbers([]);
        setChooseBoards([]);
        setSelectedNumber(null);
        setSelectBoard([]);
        
        setToast("Left the game");
        setIsToast(true);
      }
    }
  };
  


  const handleGameStatus = (state) => {
    // Show game status for all rooms
    setGameStatus(state.status);
  }





  // Debug useEffect to monitor state changes
  useEffect(() => {
  }, [choosenNumbers, selectedNumber, choosenBoards, selectBoard]);

  return (
    <>

      {isToast && <Toaster message={toast} />}
      {loading && <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading...</div>
      </div>

      }

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
  {/* Header row */}
  <div className="winning-card-row">
    {["B", "I", "N", "G", "O"].map((letter, index) => (
      <div key={index} className="winning-card-cell">
        <span>{letter}</span>
      </div>
    ))}
  </div>

  {winningCard[0] && winningCard[0].map((_, rowIndex) => (
    <div key={rowIndex} className="winning-card-row">
      {winningCard.map((row, colIndex) => {
        const cell = row[rowIndex];
        // Check win conditions
        const rowComplete = winningCard.every(r => r[rowIndex].marked);
        const colComplete = winningCard[colIndex].every(c => c.marked);
        const diagonalComplete =
          rowIndex === colIndex && winningCard.every((r, i) => r[i].marked);
        const reverseDiagonalComplete =
          rowIndex + colIndex === 4 && winningCard.every((r, i) => r[4 - i].marked);

        const fourCornersComplete =
          winningCard[0][0].marked &&
          winningCard[0][4].marked &&
          winningCard[4][0].marked &&
          winningCard[4][4].marked;

        const fourEdgesComplete =
          winningCard[0][2].marked &&
          winningCard[2][0].marked &&
          winningCard[2][4].marked &&
          winningCard[4][2].marked;

        // Does this cell belong to a winning line?
        const inWinningLine =
          (rowComplete && cell.marked) ||
          (colComplete && cell.marked) ||
          (diagonalComplete && cell.marked) ||
          (reverseDiagonalComplete && cell.marked) ||
          (fourCornersComplete &&
            cell.marked &&
            ((colIndex === 0 && (rowIndex === 0 || rowIndex === 4)) ||
             (colIndex === 4 && (rowIndex === 0 || rowIndex === 4)))) ||
          (fourEdgesComplete &&
            cell.marked &&
            ((colIndex === 0 && rowIndex === 2) ||
             (colIndex === 2 && (rowIndex === 0 || rowIndex === 4)) ||
             (colIndex === 4 && rowIndex === 2)));

        // Final background color
        let bgColor = "white";
        if (inWinningLine) {
          bgColor = "green";   // part of winning line
        } else if (cell.marked) {
          bgColor = "red";     // marked but not winning
        }

        return (
          <div
            key={colIndex}
            className="winning-card-cell"
            style={{ backgroundColor: bgColor }}
          >
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
        <>
      
          <div className="selections-container">
          <div className="balance-container">

            <div className="balance-text">
              Balance {balance.toFixed(2)} ብር
            </div>

            <div className="balance-text">
              Stake {roomId} ብር
            </div>

          
            
            {/* Connection Status */}
            <div className="connection-status">
              <div className={`status-badge ${isSocketConnected ? 'connected' : 'disconnected'}`}>
                {isSocketConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>
            
          
          </div>

          <div className="globals-container">

          {gameStatus == "waiting" && (
            <div className="countdown-container">
              <div className="countdown-text">
                {countDown !== undefined ? `Game starts in: ${countDown}` : ``}
              </div>
             
            </div>
            )}

        
        
          </div>

          <div className="numbers-grid">


            {numbers.map(number => {
              // const isPicked = pickedNumbers && pickedNumbers.includes(number) || false;
              let isPicked = false;
              if (pickedNumbers && pickedNumbers.length > 0) {
                isPicked = pickedNumbers.includes(number);
              }

              const isSelected = selectedNumber === number;
              const isChoosen = choosenNumbers.includes(number);
              // Don't disable chosen cards for unselecting, only disable if picked by another player or no connection
              const isDisabled = (isPicked && !isChoosen) || !isSocketConnected;
              const hasInsufficientBalance = balance < parseInt(roomId) || balance === 0;

              // Debug logging for selected numbers
              if (isChoosen) {
                console.log("Card",number,"is choosen")
              }

              return (
                <button
                  key={number}
                  className={`number-cell
                  ${isPicked ? 'picked' : ''}
                  ${isSelected ? 'selected' : ''}
                  ${isChoosen ? 'choosen' : ''}
                  ${isDisabled ? 'disabled' : ''}
                  ${hasInsufficientBalance ? 'insufficient-balance' : ''}
                `}
                  onClick={(e) => {
                  
                    // Prevent default to avoid any potential issues
                    e.preventDefault();
                    e.stopPropagation();
                    
                    handleNumberClick(number);
                  }}
                  onDoubleClick={() => handleNumberDoubleClick(number)}
                  disabled={isDisabled}
                  title={
                    isPicked 
                      ? `Card number ${number} is already selected by another player` 
                      : !isSocketConnected
                        ? `Please wait for connection to be established` 
                        : isChoosen
                          ? `Click to unselect card ${number} (or double-click to unselect and leave game)`
                          : `Select number ${number}`
                  }
                  aria-label={
                    isPicked 
                      ? `Number ${number} already picked` 
                      : !isSocketConnected
                        ? `Please wait for connection` 
                        : isChoosen
                          ? `Unselect card ${number}`
                          : `Select number ${number}`
                  }
                >
                  <span className='number-cell-text'>{number}</span>
                  {isPicked && <span className="picked-badge"></span>}
                </button>
              );
            })}
          </div>

          {choosenNumbers.length > 0 && selectedNumber && (
            <div className='combination-boards-container-parent'>
              <div className="combination-board-container">
               
                {/* Single Bingo Card Component */}
                <div className="combination-board">
                  <div className='card-number-container'>
                    {/* <div className='card-number'># Card {selectedNumber}</div> */}
                    <div className="combination-bingo-header">
                      {['B', 'I', 'N', 'G', 'O'].map((letter, i) => (
                        <div key={i} className="combination-bingo-header-text">{letter}</div>
                      ))}
                    </div>
                  </div>

                  <div className="board-grid-selections">
                    {selectBoard.map((row, rowIndex) => (
                      <div key={rowIndex} className="board-row-selections">
                        {row.map((num, colIndex) => (
                          <div
                            key={colIndex}
                            className={`combination-number-cell ${pickedNumbers?.length > 1 && pickedNumbers.includes(num)
                                ? 'picked-on-board'
                                : ''
                              }`}
                          >
                            {num}
                            {pickedNumbers?.length > 1 && pickedNumbers.includes(num) && (
                              <span className="picked-indicator">✓</span>
                            )}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* <div className="game-status-info">
                <p>Joined! Waiting for countdown to reach 00...</p>
                <p>Double-click your card number to leave the game</p>
              </div> */}
            </div>
          )}



        </div>
        </>
      )}





    </>
  );
};

export default Selections;