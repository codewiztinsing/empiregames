const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { submitWinner } = require('./api');  

const app = express();
app.use(cors());


// commit for github 2

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.CLIENT_URL || "http://localhost:3000",
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

// Game creator
function createGame( roomId) {
  const game = {
    id: roomId,
    players: new Map(),
    calledNumbers: [],
    currentCall: null,
    selectedNumbers: [],
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
    const intervals = gameIntervals.get(gameId);
    intervals.forEach(interval => clearInterval(interval));
    gameIntervals.delete(gameId);
  }
}

function endGame(game) {
  clearGameIntervals(game.id);
  // Clean all users from game
  game.players.clear();
  game.selectedNumbers = [];
  game.calledNumbers = [];
  game.currentCall = null;
  game.status = "waiting";
  game.gameOver = false;
  game.winner = null;
  game.countDown = 30;
  game.isCountStart = false;

  // Remove players from global users map
  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) {
      users.delete(socketId);
    }
  }

  io.to(game.roomId).emit("gameReset", {
    message: "Game ended. Preparing for next round.",
    gameId: game.id,
    roomId: game.roomId
  });

  startCountDown(game); // countdown for next round
 
}

// Countdown before starting game
function startCountDown(game) {
  console.log("game status in startCountDown  ",{
    status:game.status,
    roomId:game.roomId,
    isCountStart:game.isCountStart,
    players:game.players.size
  })
  io.emit("gameStatus", {status:game.status,roomId:game.roomId})
  if (game.isCountStart) return;
  if(game.players.size < 2) {
    console.log("trying to start count down with less 2 players")
    return
  }

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
      game.selectedNumbers = [];
      startGame(game);
    }

    game.countDown--;
  }, 1000);

  if (!gameIntervals.has(game.id)) {
    gameIntervals.set(game.id, []);
  }
  gameIntervals.get(game.id).push(countdownInterval);
}

// Game loop
function startGame(game) {



  game.status = "in-progress";
  console.log("game status in startGame  ",game.status)
  clearGameIntervals(game.id);
  io.emit("gameStatus", {status:game.status,roomId:game.roomId})

  const gameInterval = setInterval(() => {
    const calledSet = new Set(game.calledNumbers.map(b => b.number));
    let ball = generateBalls();
    while (calledSet.has(ball.number)) {
      ball = generateBalls();
    }

    game.currentCall = ball;
    game.calledNumbers.push(ball);

    io.to(game.roomId).emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: { roomId: game.roomId, numbers: game.selectedNumbers },
      total_players: game.players.size,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.roomId * game.players.size * 0.8,
      lastBall: ball,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length
    });

    if (game.calledNumbers.length >= 75) {
      io.to(game.roomId).emit("gameOver", {
        gameId: game.id,
        roomId: game.roomId,
        message: "Max number of balls reached. No winner this round."
      });
    }


  
    // createGame(game.id, game.roomId);
  }, 2000);

  if (!gameIntervals.has(game.id)) {
    gameIntervals.set(game.id, []);
  }

  io.emit("gameState", {pickedNumbers:game.selectedNumbers,roomId:game.roomId,game_status:game.status})
    
    
  gameIntervals.get(game.id).push(gameInterval);
}

// Socket events
io.on('connection', (socket) => {
  

  let game = null;
  const inProgressGames = Array.from(activeGames.values()).filter(game => game.status === 'in-progress');

  console.log("inProgressGames = ",inProgressGames)

  io.emit("activeGames", { activeGames: inProgressGames });
  if (activeGames.size > 0) {
    game = Array.from(activeGames.values())[0];
    io.emit("pickedNumbers", {roomId: game.roomId, numbers: game.selectedNumbers});

  }


  const data = {
    roomId:10
  }

  
  if(activeGames.size > 0){
    const firstGame = Array.from(activeGames.values()).find(game => game.roomId === data.roomId);
    if (firstGame) {
      io.emit("gameStatus", {status: firstGame.status, roomId: firstGame.roomId}),
      io.emit("games", {
        "game": activeGames
      });
    }



  }



  socket.on('joinGame', (data) => {

    if(!data.playerId) {
      return
    }
    if (!game) {
      game = createGame(data.roomId);
    }
  
    console.log("game status in join game ",game.status)
    // ✅ Optional: Limit max players
    if (game.players.size >= 100) {
      socket.emit('joinError', {
        message: 'Room is full (max 100 players). Please try again later.'
      });
      return;
    }

    
    if(data.playerId){
      socket.join(data.roomId);
    }
  
    if (!game.players.has(data.playerId)) {
      game.players.set(data.playerId, data.selectBoard);
    }
  
    if (!game.selectedNumbers.includes(data.selectedNumber)) {
      game.selectedNumbers.push(data.selectedNumber);
    }
  
    const playersList = Array.from(game.players.keys());
    io.emit("pickedNumbers", {
      roomId: game.roomId,
      numbers: game.selectedNumbers
    })

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
      gameId: data.gameId
    });
  
    console.log(`User ${data.playerId} joined game ${game.id}`);
  });
  
  socket.on('bingo', async (data) => {
    console.log("game id ",data)
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
        winner:data.playerId,
        calledNumbers: game.calledNumbers,
        playerCard,
        currentCall: game.currentCall,
        gameId: data.gameId,
        roomId: data.roomId
      });

      await submitWinner({
        game:game
      })

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

  socket.on('disconnect', () => {
    const user = users.get(socket.id);
    if (user) {
      const game = activeGames.get(user.gameId);
      if (game?.players.has(user.playerId)) {
        game.players.delete(user.playerId);
        // remove selected number of player from selected numbers
        game.selectedNumbers = game.selectedNumbers.filter(number => number !== user.playerId);

        io.to(game.roomId).emit("gameState", {
          "message": "user disconnected with id "+user.playerId,
          gameId: game.id,
          roomId: game.roomId,
          pickedNumbers: game.selectedNumbers,
          total_players: game.players.size,
          game_status: game.status,
          count_down: game.countDown
        });
      }
    }

    users.delete(socket.id);
    console.log(`Client disconnected: ${socket.id} (User: ${user?.playerId || 'unknown'})`);
  });
});


// Serve static files from the React build directory
app.use(express.static(path.join(__dirname, './build')));

// Handle React routing, return all requests to React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, './build', 'index.html'));
});

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
