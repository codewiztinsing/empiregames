import React, { useState, useEffect, useContext, useCallback, use } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import toast from 'react-hot-toast';

import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import checkPlayerBalance from '../api';
import axios from 'axios';
const Selections = () => {
  const {
    setToast,
    isToast,
    setIsToast,
    selectedNumber,
    setSelectedNumber,
    selectBoard,
    setSelectBoard,
    choosenNumbers,
    setChoosenNumbers,
    gameId,
    countDown,
    setCountDown,
    roomId,
    setRoomId,
    playerId,
    setPlayerId,
    playerName,
    setPlayerName,
    choosenBoards,
    setChooseBoards
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

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 400 }, (_, i) => i + 1);
  // Socket listeners with cleanup
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    setPlayerId(queryParams.get('playerId'));
    setRoomId(queryParams.get('betAmount'));
    console.log("player name = ",queryParams.get('playerName'))
    setPlayerName(queryParams.get('playerName'));
    console.log("game status = ",gameStatus)
    if(gameStatus == "active"){
      navigate("/play")
    }

    socket.emit("playerJoined", { playerId: queryParams.get('playerId'), roomId: queryParams.get('betAmount') })
   
    const handleLeaveGame = () => {
      socket.emit("leave", { 
        playerId,
        roomId,
        selectedNumber
      });
    }

 

   
    const handlePopState = () => {
      handleLeaveGame()
    
    };

    const fetchBalance = async () => {
      console.log("fetching balance")
    
      const apiUrl = process.env.REACT_APP_API_URL;
      console.log("apiUrl", apiUrl)
    
      try {
        const headers = {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        };
        const response = await axios.get(`${apiUrl}users/${queryParams.get('playerId')}`);
      
      
        setBalance(response.data.balance);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching balance:', error);
      }
    };
  
    fetchBalance();

    socket.on('gameState', handleGameState);
    socket.on('pickedNumbers', handlePickedNumbers);
    socket.on("gameStatus", handleGameStatus)

    return () => {
      socket.off('pickedNumbers', handlePickedNumbers);
      socket.off('gameState', handleGameState);
      socket.off('gameStatus', handleGameStatus);
 

    };
  }, [socket, gameId, gameStatus, choosenNumbers]);


 

  const handleGameState = (state) => {
    const gameRoom = state.roomId
    setGameStatus(state.game_status)
    console.log("current call ", state)
    setCurrentCall(state.currentCall)

    if (roomId == gameRoom) {
      setPickedNumbers(state.pickedNumbers);

      if(state.game_status == "active"){
        setGameStatus("active");
      }
      if(state.game_status == "waiting"){
        setGameStatus("waiting");
      }
      if(state.game_status == "ended"){
        setGameStatus("ended");
      }

      if(state.game_status != "active"){
        setPlayersLength(state.total_players);
      }
      setCountDown(state.count_down);
    }

  };

  socket.on('activeGames', (state) => {
    if (state?.activeGames?.length > 0) {
      const activeGameId = state.activeGames[0].id
      console.log("active game id", activeGameId)
      if (activeGameId == roomId) {
        setGameStatus("active");
      }
    }
  });



 

  socket.on('gameState', (state) => {
    if (state.roomId == roomId) {
      setPickedNumbers(state.pickedNumbers);

      if(state.game_status != "active"){
              setPlayersLength(state.total_players);

      }
      
      
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
    // return card;
    // Transpose the card array
    const transposedCard = card[0].map((_, colIndex) => 
      card.map(row => row[colIndex])
    );
    return transposedCard;


  }, []);


  const handlePickedNumbers = (state) => {
  
    if(state.roomId == roomId){
      setPickedNumbers(state.numbers);
    }
  }

  const handleBack = () => {

    navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);

    window.location.reload();
  };

  const handleStartGame = async () => {
  
  
    if (!selectedNumber || !playerId || !gameId ) return;
    setIsLoading(true);


    if (gameStatus == "active") {
      setToast("Game is already in progress");
      setIsToast(true);
      return;
    }

 


    if (balance < roomId || balance == 0) {
     
          toast.error("Insufficient balance");
          return;
     
      
    }

    try {
      socket.emit('joinGame', { playerId, gameId, selectedNumber, roomId, selectBoard, numberOfBoards: choosenBoards.length })

      navigate('/play');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      // setIsLoading(false);
    }
  };

  socket.on('joinError', (error) => {
   
    toast.error(error.message);
    setJoinError(true);
    return;
  })
  

  const handleNumberClick = (number) => {
    if (pickedNumbers && pickedNumbers.length > 0 && pickedNumbers.includes(number)) {
      toast.error("Number already picked");
      return;
    }
    if(gameStatus == "in-progress"){
      toast.error("Game is already in progress. Please wait for the next round.");
      return;
    }
    if(balance < roomId){
      toast.error("Insufficient balance");
      return;
    }
    else {
    const newBoard = generateCombination();
    setSelectBoard(newBoard);
    setSelectedNumber(number);
    try {
      socket.emit('joinGame', { playerId, gameId, selectedNumber, roomId, selectBoard, numberOfBoards: choosenBoards.length })

      navigate('/play');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      // setIsLoading(false);
    }

    }



  };
  
  const handleGameStatus = (state) => {
    console.log("state.status", state)
    setCurrentCall(state.currentCall)
    const gameRoom = state.roomId
    if (roomId == gameRoom) {
      console.log("state.status", state.game_status)
      setGameStatus(state.game_status);
    }

  }


  socket.on('pickedNumbers', handlePickedNumbers);
  socket.on('gameStatus', handleGameStatus);



  return (
    <>
  
      {loading && <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading...</div>
      </div>

      }

      {!loading && (
        <div className="selections-container">



          <div className="balance-container">
        
      
          <div className="balance-text">
          Balance {balance} ብር
            </div>
          
            <div className="balance-text">
            Stake {roomId} ብር
            </div>
            <div className="game-status">
              <div className={`status-badge ${gameStatus}`}>
                {gameStatus === 'active' ? '🟢' : '⏳'}
              </div>
            </div>

           
        
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

              return (
                <button
                  key={number}
                  className={`number-cell
                  ${isPicked ? 'picked' : ''}
                  ${isSelected ? 'selected' : ''}
                  ${isChoosen ? 'choosen' : ''}
                `}
                  onClick={() => handleNumberClick(number)}
                  disabled={isPicked}
                  aria-label={isPicked ? `Number ${number} already picked` : `Select number ${number}`}
                >
                  <span className='number-cell-text'>{number}</span>
                  {isPicked && <span className="picked-badge"></span>}
                </button>
              );
            })}
          </div>

          {selectedNumber && (
            <div className='combination-boards-container-parent'>
           
            <div className="combination-board-container">
        
              <div className="combination-board">  
                

              
             <div className='card-number-container'>
             {/* <div className='card-number'># Card {selectedNumber}</div> */}
                
                <div className="combination-bingo-header">
           
                    <div className="combination-bingo-header-text">
                      B
                    </div>
                    <div className="combination-bingo-header-text">
                      I
                    </div>
                    <div className="combination-bingo-header-text">
                      N
                    </div>
                    <div className="combination-bingo-header-text">
                      G
                    </div>
                    <div className="combination-bingo-header-text">
                      O
                    </div>
                    
                </div>
              </div>

                <div className="board-grid-selections">
                  {selectBoard.map((row, rowIndex) => (
                    
                    <div key={rowIndex} className="board-row-selections">
                      {row.map((num, colIndex) => (
                        <div
                          key={colIndex}
                          className={`combination-number-cell ${pickedNumbers && pickedNumbers.length > 1 && pickedNumbers.includes(num) ? 'picked-on-board' : ''
                            }`}
                        >
                          {num}
                          {pickedNumbers && pickedNumbers.length > 1 && pickedNumbers.includes(num) && (
                            <span className="picked-indicator">✓</span>
                          )}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
               
              </div>



         
            </div>
            {/* <button
                  className="start-game-button"
                  onClick={handleStartGame}
                >
                  {isLoading ? 'Starting...' : 'Start Game'}
              </button> */}
            </div>





          )}
        </div>
      )}





    </>
  );
};

export default Selections;