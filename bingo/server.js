// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { checkSingleCardBingo } = require('./src/helpers/singleBingo');
const { gameWinWallet,gameLossWallet,updateLastGame,getGameSettings } = require('./api');
const ip = require('ip');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
app.use(cors());
const server = http.createServer(app);


const getConstant = async () => {
  return {
    gameSpeed: 500,
    countDown: 3
  }
}

const io = socketIo(server, {
  cors: {
    origin: process.env.CLIENT_URL,
    methods: ["GET", "POST"],
    credentials: true
  },
  connectionStateRecovery: {
    maxDisconnectionDuration: 2 * 60 * 1000,
    skipMiddlewares: true
  }
});

let activeGames = new Map();
const gameIntervals = new Map();
const users = new Map();
const winners = [];

async function createGame(roomId) {
  const gameSettings = await getConstant();
  console.log("gameSettings",gameSettings)
  console.log("countDown",gameSettings.countDown)
  console.log("gameSpeed",gameSettings.gameSpeed)

  const game = {
    id: roomId,
    players: new Map(), // Map<playerId, Board[]>
    numberOfBoardsToPlayer: new Map(),
    total_players: 0,
    total_winAmount: 0, 
    calledNumbers: [],
    selectedNumbers: [],
    currentCall: null,
    status: 'waiting',
    winner: null,
    gameOver: false,
    countDown: gameSettings.countDown,
    isCountStart: false,
    gameSpeed:gameSettings.gameSpeed,
    roomId
  };
  activeGames.set(roomId, game);
  return game;
}




function clearGameIntervals(gameId) {
  if (gameIntervals.has(gameId)) {
    gameIntervals.get(gameId).forEach(clearInterval);
    gameIntervals.delete(gameId);
  }
}

async  function endGame(game) {
  clearGameIntervals(game.id);
  game.players.clear();
  game.calledNumbers = [];
  game.currentCall = null;
  game.status = "waiting";
  game.gameOver = false;
  game.winner = null;
  game.countDown = 30;
  game.isCountStart = false;

  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) users.delete(socketId);
  }

  const data = await updateLastGame(game.roomId);
  console.log("game updating data ",data)
  startCountDown(game);
}

function getWaitingGames(activeGames,status="in-progress") {
  const waitingGames = [];
  for (const game of activeGames.values()) {
    if (game.status === status) {
      // Check if this game is already in waitingGames
      const isDuplicate = waitingGames.some(existingGame => existingGame.id === game.id);
      if (isDuplicate) continue;
      waitingGames.push({
        id: game.id,
        betAmount: game.roomId,
        players: game.players.size,
        status: game.status
      });
    }
  }
  return waitingGames;
}

function startCountDown(game) {
 
  if (game.isCountStart || game.players.size < 2) return;
  clearGameIntervals(game.id);
  game.countDown = game.countDown;
  game.isCountStart = true;

  const countdownInterval = setInterval(() => {
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.total_players,
      game_status: game.status,
      count_down: game.countDown
    });

  

    if (game.countDown === 0) {
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.status = "waiting";
      game.countDown = game.countDown;
      game.currentCall = null;
      game.calledNumbers = [];
      startGame(game);
    }
    game.countDown--;
  }, 1000);

  gameIntervals.set(game.id, [countdownInterval]);
}

async function startGame(game) {
  game.status = "in-progress";
  io.emit("waitingGames",   getWaitingGames(activeGames,"in-progress"));
  clearGameIntervals(game.id);

  io.emit("gameStatus",{
    roomId: game.roomId,
    game_status: "in-progress"
  })

  const players = Array.from(game.players.keys()).map(playerId => ({
    playerId: playerId,
    numberOfBoards: game.numberOfBoardsToPlayer.get(playerId)
  }));

  game.total_players = game.total_players
  game.total_winAmount = game.selectedNumbers.length * game.roomId * 0.8

  console.log("game.total_winAmount",game.total_winAmount)



  try {
    await gameLossWallet(players, game.roomId);
  } catch (error) {
    console.error('Error charging players:', error);
  }

  const gameInterval = setInterval(() => {
    const calledSet = new Set(game.calledNumbers.map(b => b.number));
    let ball = generateBalls();
    while (calledSet.has(ball.number)) {
      ball = generateBalls();
    }
    game.currentCall = ball;
    game.calledNumbers.push(ball);
    game.selectedNumbers = [];
    io.emit("pickedNumbers",game.selectedNumbers)
  
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.roomId * game.players.size * 0.8,
      lastBall: ball,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length
    });
   

    if (game.calledNumbers.length >= 75) {
      io.emit("gameStatus", {
        roomId: game.roomId,
        game_status: "waiting"
      })
      endGame(game);
    }
  }, game.gameSpeed);
 

  gameIntervals.set(game.id, [gameInterval]);
}


function handleRefresh(data){
  console.log("handleRefresh", data)
  const game = activeGames.get(data.gameId);
  if (!game) return;
  io.to(game.roomId).emit("gameState", {
    gameId: game.id,
    roomId: game.roomId,
    total_players: game.total_players,
    pickedNumbers: game.selectedNumbers,
    game_status: game.status,
    count_down: game.countDown,
    win_amount: game.total_winAmount,
    lastBall: game.currentCall,
    called_numbers: game.calledNumbers,
    total_called_numbers: game.calledNumbers.length
  });

}


io.on('connection', (socket) => {
  socket.on("playerJoined", (data) => {
    let game = activeGames.get(data.roomId) || createGame(data.roomId);
    const inProgressGames = [...activeGames.values()].filter(g => g.status === 'in-progress');
    socket.emit("activeGames", { activeGames: inProgressGames });
    socket.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  });

  
  const waitingGames = getWaitingGames(activeGames, "waiting");
  const inProgressGames = getWaitingGames(activeGames, "in-progress");
  socket.emit("waitingGames", [...waitingGames, ...inProgressGames]);

  socket.on("handleRefresh",handleRefresh)
  


  socket.emit("waitingGames", waitingGames);

  socket.on("joinGame", (data) => {

    const game = activeGames.get(data.roomId);
    if (!data.playerId || !game) return;

    if (game.status === 'in-progress') {
      socket.emit('joinError', {
        roomId: data.roomId,
        message: 'Game is already in progress. Please wait for the next round.'
      });
      return;
    }

    if (game.players.has(data.playerId)) {
      socket.emit('joinError', {
        roomId: data.roomId,
        message: 'Already in game. Finish or leave current game.'
      });
      return;
    }

    game.selectedNumbers.push(data.selectedNumber)
    game.selectedNumbers.push(data.selectedNumber2)
    game.numberOfBoardsToPlayer.set(data.playerId,data.numberOfBoards)
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
    if (game.players.size >= 100) {
      socket.emit('joinError', {
        message: 'Room is full (max 100 players).'
      });
      return;
    }

    const total_players = game.selectedNumbers.filter(num => num !== null).length
    const win_amount = total_players * game.roomId * 0.8
    game.total_winAmount = win_amount
    game.total_players = total_players


    socket.join(data.roomId);

    const boards = [data.selectBoard];
    if (data.selectBoard2) {
      boards.push(data.selectBoard2);
    }
    game.players.set(data.playerId, boards);

  
  
    const playersList = [...game.players.keys()];
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.total_players,
      game_status: game.status,
      count_down: game.countDown,
      players: playersList
    });

    if (!game.isCountStart && game.players.size >= 2) {
      startCountDown(game);
    }

    users.set(socket.id, {
      playerId: data.playerId,
      roomId: data.roomId,
      gameId: data.roomId
    });


    const waitingGames = getWaitingGames(activeGames,"waiting");
    io.emit("waitingGames",waitingGames)
   

  });
  

  socket.on("bingo", async (data) => {
    const game = activeGames.get(data.gameId);
    if (!game || game.status !== 'in-progress') return;


    const playerCards = game.players.get(data.playerId);
    if (!playerCards || !Array.isArray(playerCards)) return;
    const board = data.board
    const boardNumber = data.boardNumber
    console.log("boardNumber ",boardNumber)
    const markedSingleCard = markPlayerCard(board, game.calledNumbers)
    const isSingleBingo = checkSingleCardBingo(markedSingleCard)
    if(isSingleBingo){

      io.to(game.roomId).emit("winBingo", {
            isBingo: true,
            playerId: data.playerId,
            markedCells: markedSingleCard,
            winningCard: markedSingleCard,
            winner: data.playerId,
            calledNumbers: game.calledNumbers,
            playerCard: boardNumber,
            winner_Number: boardNumber,
            playerName: data.playerName,
            currentCall: game.currentCall,
            gameId: data.gameId,
            total_winAmount: game.total_winAmount,
            total_players: game.total_players,
            roomId: data.roomId
      })

      try {
        await gameWinWallet(data.playerId, game.roomId, game.total_winAmount);
      } catch (error) {
        console.error("Error processing win wallet:", error);
      }

      endGame(game);
    }

    else{
      io.to(game.roomId).emit("falseBingo", {
        isBingo: false,
        playerId: data.playerId,
        losser_board: boardNumber,
      })
    }
      

  
    
});
  
//   socket.on("bingo", async (data) => {
//     const game = activeGames.get(data.gameId);
//     if (!game || game.status !== 'in-progress') return;

//     const playerCards = game.players.get(data.playerId);
//     if (!playerCards || !Array.isArray(playerCards)) return;

//     console.log("Checking bingo for player:", data.playerId, "with cards:", playerCards);

//     const isBingo = checkBingo(playerCards, game.calledNumbers);
    
//     if (isBingo) {
//         // Game over logic
//         game.status = 'waiting';
//         game.winner = data.playerId;
//         game.gameOver = true;

//         // Find the winning card (the first one that has a bingo)
//         const winningCard = playerCards.find(card => {
//             const markedCard = markPlayerCard(card, game.calledNumbers);
//             return checkSingleCardBingo(markedCard);
//         }) || playerCards[0]; // Fallback to first card if none found (shouldn't happen)

//         const markedWinningCard = markPlayerCard(winningCard, game.calledNumbers);

//         console.log(`Bingo confirmed for player ${data.playerName} (${data.playerId})`);

//         // Emit win event
//         io.to(game.roomId).emit("winBingo", {
//             isBingo: true,
//             playerId: data.playerId,
//             markedCells: markedWinningCard,
//             winningCard: markedWinningCard,
//             winner: data.playerId,
//             calledNumbers: game.calledNumbers,
//             playerCard: winningCard,
//             winner_Number: data.selectedNumber,
//             playerName: data.playerName,
//             currentCall: game.currentCall,
//             gameId: data.gameId,
//             total_winAmount: game.total_winAmount,
//             total_players: game.total_players,
//             roomId: data.roomId
//         });

//         // Record winner and process payout
//         winners.push({ 
//             roomId: game.roomId, 
//             winner: data.playerId, 
//             time: new Date(),
//             winAmount: game.total_winAmount
//         });
        
//         try {
//             await gameWinWallet(data.playerId, game.roomId, game.total_winAmount);
//         } catch (error) {
//             console.error("Error processing win wallet:", error);
//             // Handle error (maybe notify admin)
//         }
        
//         endGame(game);
//     } else {
//         console.log(`False bingo called by player ${data.playerName} (${data.playerId})`);
        
//         io.to(game.roomId).emit("falseBingo", {
//             isBingo: false,
//             playerId: data.playerId,
//             calledNumbers: game.calledNumbers,
//             currentCall: game.currentCall,
//             gameId: data.gameId,
//             total_winAmount: game.total_winAmount,
//             total_players: game.total_players,
//             roomId: data.roomId,
//             playerName: data.playerName  // Added for consistency
//         });
//     }
// });

// Helper function to check bingo for a single card
// function checkSingleCardBingo(markedCard) {
//     // Check rows
//     for (let row = 0; row < 5; row++) {
//         if (markedCard[row].every(cell => cell.marked || cell === '*')) return true;
//     }

//     // Check columns
//     for (let col = 0; col < 5; col++) {
      
//         if (markedCard.every(row => row[col].marked || row[col] === '*')) return true;

//     }

//     // Check diagonals
//     if (markedCard[0][0].marked && markedCard[1][1].marked && 
//         markedCard[2][2].marked && markedCard[3][3].marked && markedCard[4][4].marked) {
//         return true;
//     }
//     if (markedCard[0][4].marked && markedCard[1][3].marked && 
//         markedCard[2][2].marked && markedCard[3][1].marked && markedCard[4][0].marked) {
//         return true;
//     }

//     // Check four corners
//     if (markedCard[0][0].marked && markedCard[0][4].marked &&
//         markedCard[4][0].marked && markedCard[4][4].marked) {
//         return true;
//     }

//     return false;
// }
  

  // socket.on("bingo", async (data) => {
  //   const game = activeGames.get(data.gameId);
  //   if (!game || game.status !== 'in-progress') return;
  //   const playerCards = game.players.get(data.playerId);
  //   console.log("playerCards",playerCards)
  //   if (!playerCards) return;

  //   console.log("playerCards", playerCards)

  //   const isBingo = checkBingo(playerCards, game.calledNumbers);
  //   if (isBingo) {
  //     game.status = 'waiting';
  //     game.winner = data.playerId;
  //     game.gameOver = true;

  //     let winnedCard = []

  //     for(let i = 0; i < playerCards.length; i++){
  //       winnedCard = playerCards[i]
  //     }

  //     console.log("playerName: data.playerName,",data.playerName,)

  //     io.to(game.roomId).emit("winBingo", {
  //       isBingo: true,
  //       playerId: data.playerId,
  //       markedCells: markPlayerCard(winnedCard, game.calledNumbers),
  //       winningCard: markPlayerCard(winnedCard, game.calledNumbers),
  //       winner: data.playerId,
  //       calledNumbers: game.calledNumbers,
  //       playerCard: winnedCard,
  //       winner_Number: data.selectedNumber,
  //       playerName: data.playerName,
  //       currentCall: game.currentCall,
  //       gameId: data.gameId,
  //       total_winAmount: game.total_winAmount,
  //       total_players: game.total_players,
  //       roomId: data.roomId
  //     });

     
  //     winners.push({ roomId: game.roomId, winner: data.playerId, time: new Date() });
  //     await gameWinWallet(data.playerId,game.roomId,game.total_winAmount);
  //     endGame(game);
  //   } else {
  //     io.to(game.roomId).emit("falseBingo", {
  //       isBingo: false,
  //       playerId: data.playerId,
  //       calledNumbers: game.calledNumbers,
  //       currentCall: game.currentCall,
  //       gameId: data.gameId,
  //       total_winAmount: game.total_winAmount,
  //       total_players: game.total_players,
  //       roomId: data.roomId
  //     });
  //   } 
     
  // });

  socket.on("leave",(data) => {
    const game = activeGames.get(data.roomId);
    const playerId = data.playerId;
    console.log("playerId",playerId)
    // remove this playerId from game
    if (game?.players.has(playerId)) {
      game.players.delete(playerId);
    }
  
    
    const selectedCard = data.selectedNumber
    const selectedCard2 = data.selectedNumber2
    if (!game) return;
    if (selectedCard && game.selectedNumbers.includes(selectedCard)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard);
    }
    if (selectedCard2 && game.selectedNumbers.includes(selectedCard2)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard2);
    }
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  
    io.emit("waitingGames",   [...getWaitingGames(activeGames),...getWaitingGames(activeGames,"waiting")]);
    
  })

  socket.on("getWinners", () => {
    socket.emit("winners", winners);
  });

  socket.on("disconnect", () => {
    const user = users.get(socket.id);
  
    if (user) {
      const game = activeGames.get(user.gameId);
      console.log("user diconnect from game ",game.roomId,game.status)
      if (game?.players.has(user.playerId)) {
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          io.to(game.roomId).emit("gameState", {
            message: `User ${user.playerId} disconnected`,
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers,
            total_players: game.total_players,
            game_status: game.status,
            count_down: game.countDown
          });
          users.delete(socket.id);
        }
       
    }
    }
  });
});

app.use(express.static(path.join(__dirname, './build')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, './build', 'index.html'));
});

const PORT = process.env.SERVER_PORT
const IP = ip.address();
server.listen(PORT, () => console.log(`Server running on port ${PORT} and IP ${IP}`));



