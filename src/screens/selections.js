import React, { useState, useEffect, useContext, useCallback, use } from 'react';
import { SocketContext } from '../contexts/socket';
import Toaster from '../components/Toaster';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import checkPlayerBalance from '../api';

const Selections = () => {
  const { 
          selectedNumber,
          setSelectedNumber, 
          selectBoard,
          setSelectBoard,
          gameId,
          countDown,
          setCountDown, 
          roomId, 
          setRoomId,
          playerId, 
          setPlayerId,
          playerCard,
          setPlayerCard,
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
  const [currentCall,setCurrentCall] = useState(null);
  const [gameStatus,setGameStatus] = useState("waiting");
  const [joinError,setJoinError] = useState(false);
  const [balance,setBalance] = useState(0);

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 100 }, (_, i) => i + 1);

  // Socket listeners with cleanup
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    setPlayerId(queryParams.get('playerId'));
    setRoomId(queryParams.get('betAmount'));
    socket.emit("playerJoined",{playerId:queryParams.get('playerId'),roomId:queryParams.get('betAmount')})

    const fetchBalance = async () => {
      try {
        const response = await fetch(`https://api.bilenbingo.com/payments/balance/?user_id=${queryParams.get('playerId')}`);
      
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("data",data)
        setBalance(data.balance);
      } catch (error) {
        console.error('Error fetching balance:', error);
      }
    };

    fetchBalance();
  
    socket.on('gameState', handleGameState);
    socket.on('pickedNumbers', handlePickedNumbers);
    socket.on("gameStatus",handleGameStatus)
    return () => {
      // socket.off('pickedNumbers', handlePickedNumbers);
      socket.off('gameState', handleGameState);
    };
  }, [socket, gameId,gameStatus]);




  const handleGameState = (state) => {
    const gameRoom = state.roomId
    if(roomId == gameRoom){
      setPickedNumbers(state.pickedNumbers.numbers);
      setPlayersLength(state.total_players);
      setCountDown(state.count_down);
    }

  };

  socket.on('activeGames', (state) => {
    if(state?.activeGames?.length > 0){
      const activeGameId = state.activeGames[0].id
      console.log("active game id", activeGameId)
      if(activeGameId == roomId){
        setGameStatus("in-progress");
      }
    }
  
    
  
  });

  socket.on('gameState', (state) => {
    if(state.roomId == roomId){
    setPickedNumbers(state.pickedNumbers.numbers);
    setPlayersLength(state.total_players);
    setCountDown(state.count_down);
    }
  });



  // Memoized board generation
  const generateCombination = useCallback(() => {
    const card = [];
    const ranges = [
      [1, 15],    // B
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
    return card;
  }, []);


  const handlePickedNumbers = (state) => {
    console.log("state = ", state)
    if(state.roomId == roomId) {
      setPickedNumbers(state.numbers);
    }

  }
  

  const handleStartGame = async () => {
    if (!selectedNumber || !playerId || !gameId) return;
    // setIsLoading(true);
    if(gameStatus == "in-progress"){
      setToast("Game is already in progress");
      setIsToast(true);
      return;
    }



   

    
    try {

     
        socket.emit('joinGame', { playerId, gameId, selectedNumber, roomId, selectBoard });
    

    
      navigate('/play');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      // setIsLoading(false);
    }
  };

  socket.on('joinError', (error) => {
    console.log("error",error)
    setToast(error.message);
    setIsToast(true);
    setJoinError(true);
    return;
  })

  const handleNumberClick = (number) => {
    if (pickedNumbers && pickedNumbers.length > 0 &&pickedNumbers.includes(number)) return;
    const newBoard = generateCombination();
    console.log("number = ",number)
    setSelectedNumber(number);
    setSelectBoard(newBoard);
  };

  const handleGameStatus = (state) => {
    console.log("state",state)
    const gameRoom = state.roomId
    if(roomId == gameRoom){
      setGameStatus(state.status);
    }

  }


  socket.on('pickedNumbers', handlePickedNumbers);
  socket.on('gameStatus', handleGameStatus);




  return (
    <>

   

    {isToast && <Toaster message={toast} />}
    <div className="selections-container">

    <div className="balance-container">
      <div className="balance-text">
        Balance: {balance}
      </div>
      <div className="balance-text">
        Stake {roomId}
      </div>
    </div>
      <div className="game-status">
        <div className={`status-badge ${gameStatus}`}>
          {gameStatus}
        </div>
      </div>

      <div className="numbers-grid">

        
        {numbers.map(number => {
          // const isPicked = pickedNumbers && pickedNumbers.includes(number) || false;
          let isPicked = false;
          if(pickedNumbers && pickedNumbers.length > 0){
            isPicked = pickedNumbers.includes(number);
          }

          const isSelected = selectedNumber === number;
          
          return (
            <button
              key={number}
              className={`number-cell 
                ${isPicked ? 'picked' : ''}
                ${isSelected ? 'selected' : ''}
              `}
              onClick={() => handleNumberClick(number)}
              disabled={isPicked}
              aria-label={isPicked ? `Number ${number} already picked` : `Select number ${number}`}
            >
              {number}
              {isPicked && <span className="picked-badge">Picked</span>}
            </button>
          );
        })}
      </div>

      {selectedNumber && (
        <div className="combination-board">
         
          <div className="board-grid">
            {selectBoard.map((row, rowIndex) => (
              <div key={rowIndex} className="board-row">
                {row.map((num, colIndex) => (
                  <div 
                    key={colIndex} 
                    className={`board-cell ${
                      pickedNumbers && pickedNumbers.length > 1 && pickedNumbers.includes(num) ? 'picked-on-board' : ''
                    }`}
                  >
                    {num}
                    {  pickedNumbers && pickedNumbers.length > 1 && pickedNumbers.includes(num) && (
                      <span className="picked-indicator">✓</span>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
          <button
            className="start-game-button"
            onClick={handleStartGame}
          >
            {isLoading ? 'Starting...' : 'Start Game'}
          </button>
        </div>
      )}
    </div>
    </>
  );
};

export default Selections;