// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { gameWinWallet,gameLossWallet } = require('./api');

const app = express();
app.use(cors());
const server = http.createServer(app);

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

function createGame(roomId) {
  const game = {
    id: roomId,
    players: new Map(),
    calledNumbers: [],
    selectedNumbers: [],
    currentCall: null,
    status: 'waiting',
    winner: null,
    gameOver: false,
    countDown: 30,
    isCountStart: false,
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

function endGame(game) {
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

  io.to(game.roomId).emit("gameReset", {
    message: "Game ended. Preparing for next round.",
    gameId: game.id,
    roomId: game.roomId
  });
  startCountDown(game);
}

function getWaitingGames(activeGames) {
  const waitingGames = [];
  for (const game of activeGames.values()) {
    if (game.status === 'waiting') {
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
  game.countDown = 30;
  game.isCountStart = true;

  const countdownInterval = setInterval(() => {
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.players.size,
      game_status: game.status,
      count_down: game.countDown
    });

    if (game.countDown === 0) {
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.status = "waiting";
      game.countDown = 30;
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
  clearGameIntervals(game.id);

  io.emit("gameStatus",{
    roomId: game.roomId,
    game_status: "in-progress"
  })

  const players = Array.from(game.players.keys()).map(playerId => ({
    playerId: playerId
  }));
  try {
    await gameLossWallet(players, game.roomId, game.id);
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
      total_players: game.players.size,
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
  }, 3000);

  gameIntervals.set(game.id, [gameInterval]);
}

io.on('connection', (socket) => {
  socket.on("playerJoined", (data) => {
    let game = activeGames.get(data.roomId) || createGame(data.roomId);
    const inProgressGames = [...activeGames.values()].filter(g => g.status === 'in-progress');
    socket.emit("activeGames", { activeGames: inProgressGames });
    socket.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  });

  const waitingGames = getWaitingGames(activeGames);


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
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
   
 
    if (game.players.size >= 100) {
      socket.emit('joinError', {
        message: 'Room is full (max 100 players).'
      });
      return;
    }

    socket.join(data.roomId);
    game.players.set(data.playerId, data.selectBoard);
    

    const playersList = [...game.players.keys()];
    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.players.size,
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

    io.emit("waitingGames",   getWaitingGames(activeGames));
    console.log("waiting game s",getWaitingGames(activeGames))
  });
  

  socket.on("bingo", async (data) => {
    const game = activeGames.get(data.gameId);
    if (!game || game.status !== 'in-progress') return;
    const playerCard = game.players.get(data.playerId);
    if (!playerCard) return;

    const isBingo = checkBingo(playerCard, game.calledNumbers);
    if (isBingo) {
      game.status = 'waiting';
      game.winner = data.playerId;
      game.gameOver = true;

      io.to(game.roomId).emit("winBingo", {
        isBingo: true,
        playerId: data.playerId,
        markedCells: markPlayerCard(playerCard, game.calledNumbers),
        winningCard: markPlayerCard(playerCard, game.calledNumbers),
        winner: data.playerId,
        calledNumbers: game.calledNumbers,
        playerCard,
        currentCall: game.currentCall,
        gameId: data.gameId,
        roomId: data.roomId
      });

      winners.push({ roomId: game.roomId, winner: data.playerId, time: new Date() });
      await gameWinWallet(data.playerId,game.roomId * game.players.size * 0.8,game.id);
      endGame(game);
    } else {
      io.to(game.roomId).emit("falseBingo", {
        isBingo: false,
        playerId: data.playerId,
        markedCells: markPlayerCard(playerCard, game.calledNumbers),
        calledNumbers: game.calledNumbers,
        playerCard,
        currentCall: game.currentCall,
        gameId: data.gameId,
        roomId: data.roomId
      });
    }
  });

  socket.on("leave",(data) => {
    const game = activeGames.get(data.roomId);
    const selectedCard = data.selectedNumber
    if (!game) return;
    if (selectedCard && game.selectedNumbers.includes(selectedCard)) {
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedCard);
    }
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  
    io.emit("waitingGames",   getWaitingGames(activeGames));
    
  })

  socket.on("getWinners", () => {
    socket.emit("winners", winners);
  });

  socket.on("disconnect", () => {
    const user = users.get(socket.id);
    if (user) {
      const game = activeGames.get(user.gameId);
      if (game?.players.has(user.playerId)) {
        game.players.delete(user.playerId);
        io.to(game.roomId).emit("gameState", {
          message: `User ${user.playerId} disconnected`,
          gameId: game.id,
          roomId: game.roomId,
          pickedNumbers: game.selectedNumbers,
          total_players: game.players.size,
          game_status: game.status,
          count_down: game.countDown
        });
      }
      users.delete(socket.id);
    }
  });
});

app.use(express.static(path.join(__dirname, './build')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, './build', 'index.html'));
});

const PORT = process.env.SERVER_PORT || 5000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));



