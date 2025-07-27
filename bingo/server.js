// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { handleJoin } = require('./src/helpers/handleJoin');
const { getWaitingGames } = require('./src/helpers/getWaitingGames');
const { clearGameIntervals } = require('./src/helpers/handleClearGameIntervals');
const { startCountDown } = require('./src/helpers/handleStartCountDown');
const { endGame } = require('./src/helpers/endGame');
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
    countDown: 10
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


  const game = {
    id: roomId,
    players: new Map(), // Map<playerId, Board[]>
    numberOfBoardsToPlayer: new Map(),
    selectedNumbersToPlayer: new Map(),
    playersLeftBeforeStart:[],
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
    handleJoin(io,socket,data,activeGames,users,gameIntervals)
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
        const total_players = game.selectedNumbers.length
        
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



  socket.on("leave",(data) => {
    const game = activeGames.get(data.roomId);
    const playerId = data.playerId;
    

    if (game?.players.has(playerId)) {
      game.players.delete(playerId);
    }
  
    
    const selectedCard = data.selectedNumber
    const selectedCard2 = data.selectedNumber2

    console.log("selectedCard",selectedCard)
    console.log("selectedCard2",selectedCard2)
    if (!game) return;
    if (selectedCard && game.selectedNumbers.includes(selectedCard)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard);
    }
    if (selectedCard2 && selectedCard2 !== null && game.selectedNumbers.includes(selectedCard2)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard2 && num !== null);
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
      if (game?.players.has(user.playerId)) {
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          game.playersLeftBeforeStart.push(user.playerId)
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



