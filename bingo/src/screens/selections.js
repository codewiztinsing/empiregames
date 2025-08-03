import React, { useState, useEffect, useContext, useCallback, use } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import Toaster from '../components/Toaster';
import './selections.css';
import { useNavigate } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import checkPlayerBalance from '../api';
import axios from 'axios';
const Selections = () => {
  const {
    selectedNumber,
    selectedNumber2,
    setSelectedNumber,
    setSelectedNumber2,
    selectBoard,
    setSelectBoard,
    selectBoard2,
    setSelectBoard2,
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

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 400 }, (_, i) => i + 1);
  // Socket listeners with cleanup
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    setPlayerId(queryParams.get('playerId'));
    setRoomId(queryParams.get('betAmount'));
    console.log("player name = ",queryParams.get('playerName'))
    setPlayerName(queryParams.get('playerName'));

    socket.emit("playerJoined", { playerId: queryParams.get('playerId'), roomId: queryParams.get('betAmount') })
    // Listen for page visibility changes
    const handleVisibilityChange = () => {
        socket.emit("leaveGame", { 
          playerId,
          roomId,
          selectedNumber,
          selectedNumber2
        });
      
    };

    const handleBackChange = () => {
      console.log("back button clicked")
      socket.emit("leaveGame", { 
        playerId,
        roomId,
        selectedNumber,
        selectedNumber2
      });
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener('popstate', handleBack);
  

    const fetchBalance = async () => {
      console.log("fetching balance")
    
      const apiUrl = process.env.REACT_APP_API_URL;
      console.log("apiUrl", apiUrl)
    
      try {
        const headers = {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        };
        const response = await axios.get(`${apiUrl}wallet/player/${queryParams.get('playerId')}`);
      
      
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
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener('popstate', handleBackChange);
    };
  }, [socket, gameId, gameStatus, choosenNumbers]);




  const handleGameState = (state) => {
    const gameRoom = state.roomId

    if (roomId == gameRoom) {
      setPickedNumbers(state.pickedNumbers.numbers);

      if(state.game_status == "in-progress"){
        setGameStatus("in-progress");
      }
      if(state.game_status == "waiting"){
        setGameStatus("waiting");
      }
      if(state.game_status == "ended"){
        setGameStatus("ended");
      }

      if(state.game_status != "in-progress"){
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
        setGameStatus("in-progress");
      }
    }
  });

  socket.on('gameState', (state) => {
    if (state.roomId == roomId) {
      setPickedNumbers(state.pickedNumbers);

      if(state.game_status != "in-progress"){
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
    // setIsLoading(true);

    if (gameStatus == "in-progress") {
      setToast("Game is already in progress");
      setIsToast(true);
      return;
    }

 
    if(selectedNumber2) {
      if(balance < roomId * 2) {
        setToast("Insufficient balance for two cards,please select one card");
        setIsToast(true);
        return;
      }
    }

    if (balance < roomId || balance == 0) {
     
          setToast("Insufficient balance");
          setIsToast(true);
          return;
     
      
    }

    try {
      socket.emit('joinGame', { playerId, gameId, selectedNumber,selectedNumber2, roomId, selectBoard, selectBoard2, numberOfBoards: choosenBoards.length })

      navigate('/play');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      // setIsLoading(false);
    }
  };

  socket.on('joinError', (error) => {
   
    setToast(error.message);
    setIsToast(true);
    setJoinError(true);
    return;
  })
  

  const handleNumberClick = (number) => {
    if (pickedNumbers && pickedNumbers.length > 0 && pickedNumbers.includes(number)) {
      return;
    }

    // If number is already chosen, remove it
    if (choosenNumbers.includes(number)) {
      const index = choosenNumbers.indexOf(number);
      if (index > -1) {
        const newNumbers = [...choosenNumbers];
        const newBoards = [...choosenBoards];
        newNumbers.splice(index, 1);
        newBoards.splice(index, 1);
        setChoosenNumbers(newNumbers);
        setChooseBoards(newBoards);
        
        // Update the appropriate selected number and board
        if (index === 0) {
          setSelectedNumber(null);
          setSelectBoard([]);
        } else {
          setSelectedNumber2(null); 
          setSelectBoard2([]);
        }
      }
      return;
    }

    // Only allow selecting up to 2 numbers
    if (choosenNumbers.length >= 2) {
      return;
    }

    // Add new number and generate new board
    const newNumbers = [...choosenNumbers, number];
    const newBoard = generateCombination();

    setChoosenNumbers(newNumbers);
    
    // Set appropriate selected number and board based on position
    if (newNumbers.length === 1) {
      setSelectedNumber(number);
      setSelectBoard(newBoard);
      setChooseBoards([newBoard]);
    } else {
      setSelectedNumber2(number);
      setSelectBoard2(newBoard);
      setChooseBoards([...choosenBoards, newBoard]);
    }

  
  };
  
  const handleGameStatus = (state) => {
    // console.log("state", state)
    const gameRoom = state.roomId
    if (roomId == gameRoom) {
      setGameStatus(state.status);
    }

  }


  socket.on('pickedNumbers', handlePickedNumbers);
  socket.on('gameStatus', handleGameStatus);



  return (
    <>

      {isToast && <Toaster message={toast} />}
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
                {gameStatus}
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
             <div className='card-number'># Card {selectedNumber}</div>
                
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



           
            {selectedNumber2 && (
              <div className="combination-board">  
                <div className='card-number-container'>
                <div className='card-number'># Card {selectedNumber2}</div>
                
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
                    {selectBoard2.map((row, rowIndex) => (
                      
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
            )}


           
         
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
      )}





    </>
  );
};

export default Selections;