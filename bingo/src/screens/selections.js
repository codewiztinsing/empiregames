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
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [totalCalledNumbers, setTotalCalledNumbers] = useState(0);
  const [totalWinAmount, setTotalWinAmount] = useState(0);
  const [isBingo, setIsBingo] = useState(false);
  const [winnerCardNumber, setWinnerCardNumber] = useState(null);
  const [winnerPlayerName, setWinnerPlayerName] = useState(null);
  const [winningCard, setWinningCard] = useState([]);

  // Generate numbers 1-100 (memoized since it's static)
  const numbers = Array.from({ length: 400 }, (_, i) => i + 1);

  // Socket listeners with cleanup
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    setPlayerId(queryParams.get('playerId'));
    setRoomId(queryParams.get('betAmount'));
    setPlayerName(queryParams.get('playerName'));


    socket.emit("playerJoined", { playerId: queryParams.get('playerId'), roomId: queryParams.get('betAmount') })

    const fetchBalance = async () => {
      const apiUrl = process.env.REACT_APP_API_URL;
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
    socket.on("bingoWinner", handleBingoWinner)

     if (isBingo) {
      const timer = setTimeout(() => {
        setIsBingo(false);
      }, 5000);
      return () => clearTimeout(timer);
     }

    return () => {
      // socket.off('pickedNumbers', handlePickedNumbers);
      socket.off('gameState', handleGameState);
    };
  }, [socket, gameId, gameStatus, choosenNumbers]);


const handleGlobals = (state) => {

  if (state.roomId == roomId) {
  setCountDown(state.countDown);
  if (state.lastBall && state.lastBall?.number) {
    setCurrentCall(state.lastBall?.number);
  }
 

  setTotalPlayers(state.totalPlayers);
    setTotalCalledNumbers(state.totalCalledNumbers);
    setTotalWinAmount(state.totalWinAmount);
  }
}

  const handleBingoWinner = (state) => {
    console.log("bingoWinner",state)
    setIsBingo(true);
    setWinnerCardNumber(state.winnerCardNumber);
    setWinnerPlayerName(state.winnerPlayerName);
    setWinningCard(state.winningCard);
  }

  const handleGameState = (state) => {
    console.log("gameState",state)
    const gameRoom = state.roomId
    if (roomId == gameRoom) {
      if (state.pickedNumbers !== null) {
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
      setCountDown(state.count_down);
    }

  };

  socket.on('globals', handleGlobals);

  socket.on('activeGames', (state) => {
    if (state?.activeGames?.length > 0) {
      const activeGameId = state.activeGames[0].id
      if (activeGameId == roomId) {
        setGameStatus("in-progress");
      }
    }



  });

  socket.on('gameState', (state) => {
    if (state.roomId == roomId) {
      if (state.pickedNumbers !== null) {
        setPickedNumbers(state.pickedNumbers.numbers);
      }

      if (state.game_status != "in-progress") {
        setPlayersLength(state.total_players);

      }
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
    if (state.roomId == roomId) {
      setPickedNumbers(state.numbers);
    }

  }

  const handleBack = () => {

    navigate(`/?playerId=${playerId}&&betAmount=${roomId}`);

    window.location.reload();
  };

  const handleStartGame = async () => {
    if (!selectedNumber || !playerId || !gameId) return;
    // setIsLoading(true);
    if (gameStatus == "in-progress") {
      setToast("Game is already in progress");
      setIsToast(true);
      return;
    }

    if (balance < parseInt(roomId) || balance == 0) {
      setToast("Insufficient balance");
      setIsToast(true);
      return;
    }
    if (balance < parseInt(roomId) * choosenBoards.length) {
      setToast("Insufficient balance");
      setIsToast(true);
      return;
    }

    try {
      socket.emit('joinGame', { playerId, gameId, selectedNumber, selectedNumber2, roomId, selectBoard, selectBoard2, numberOfBoards: choosenBoards.length })

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
  
        // Rebalance cards after removal
        if (newNumbers.length === 0) {
          setSelectedNumber(null);
          setSelectBoard([]);
          setSelectedNumber2(null);
          setSelectBoard2([]);
        } else if (newNumbers.length === 1) {
          // Only one card left → it becomes the first
          setSelectedNumber(newNumbers[0]);
          setSelectBoard(newBoards[0]);
          setSelectedNumber2(null);
          setSelectBoard2([]);
        } else {
          // Two cards remain → reset both
          setSelectedNumber(newNumbers[0]);
          setSelectBoard(newBoards[0]);
          setSelectedNumber2(newNumbers[1]);
          setSelectBoard2(newBoards[1]);
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
    const newBoards = [...choosenBoards, newBoard];
  
    setChoosenNumbers(newNumbers);
    setChooseBoards(newBoards);
  
    // Rebalance after adding
    if (newNumbers.length === 1) {
      setSelectedNumber(newNumbers[0]);
      setSelectBoard(newBoards[0]);
    } else if (newNumbers.length === 2) {
      setSelectedNumber(newNumbers[0]);
      setSelectBoard(newBoards[0]);
      setSelectedNumber2(newNumbers[1]);
      setSelectBoard2(newBoards[1]);
    }
  };
  


  const handleGameStatus = (state) => {
    console.log("gameStatus", state)
    const gameRoom = state.roomId
    if (roomId == gameRoom) {
      setGameStatus(state.status);
    }

  }


  socket.on('pickedNumbers', handlePickedNumbers);
  socket.on('gameStatus', handleGameStatus);
  socket.on("gameState", handleGameState);



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

          <div className="globals-container">

          {gameStatus == "waiting" && (
            
            <div className="game-info-text">
              countDown {countDown}
            </div>
            )}

        
          {gameStatus == "in-progress" && (
            
           <>
           <div className="global-ball-container">
            <div className="global-ball">
              Ball {currentCall}
            </div>
           </div>
            <div className="game-info-text">
              Total players {totalPlayers}
            </div>

           
           
           </>

            
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

          {choosenNumbers.length > 0 && (selectedNumber || selectedNumber2) && (
            <div className='combination-boards-container-parent'>
              <div className="combination-board-container">
               

                {/* Reusable Bingo Card Component */}
                {[{ number: selectedNumber, board: selectBoard }, { number: selectedNumber2, board: selectBoard2 }]
                  .filter(item => item.number) // render only if number exists
                  .map((item, idx) => (
                    <div key={idx} className="combination-board">
                      <div className='card-number-container'>
                        <div className='card-number'># Card {item.number}</div>
                        <div className="combination-bingo-header">
                          {['B', 'I', 'N', 'G', 'O'].map((letter, i) => (
                            <div key={i} className="combination-bingo-header-text">{letter}</div>
                          ))}
                        </div>
                      </div>

                      <div className="board-grid-selections">
                        {item.board.map((row, rowIndex) => (
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
                  ))
                }

              </div>

              <button className="start-game-button" onClick={handleStartGame}>
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