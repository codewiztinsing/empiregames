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
const { handleLeave } = require('./src/helpers/handleLeave');
const { checkSingleCardBingo } = require('./src/helpers/singleBingo');
const { createGame } = require('./src/helpers/handleCreateGame');
const {handleBingo} = require('./src/helpers/handleBingo');
const { handleRefresh } = require('./src/helpers/handleRefresh');
const { handleDisconnect } = require('./src/helpers/handleDisconnect');
const ip = require('ip');
const dotenv = require('dotenv');
dotenv.config();
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


io.on('connection', (socket) => {
  socket.on("playerJoined", (data) => {
    let game = activeGames.get(data.roomId) || createGame(data.roomId,activeGames);
    const inProgressGames = [...activeGames.values()].filter(g => g.status === 'in-progress');
    socket.emit("activeGames", { activeGames: inProgressGames });
    socket.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  });

  
  const waitingGames = getWaitingGames(activeGames, "waiting");
  const inProgressGames = getWaitingGames(activeGames, "in-progress");
  socket.emit("waitingGames", [...waitingGames, ...inProgressGames]);

  socket.on("handleRefresh",(data)=>handleRefresh(data,activeGames,io))
  


  socket.emit("waitingGames", waitingGames);
  socket.on("joinGame", (data) => {
    handleJoin(io,socket,data,activeGames,users,gameIntervals)
  });
  
  socket.on("bingo", (data) => {
    handleBingo(data,activeGames,io,gameIntervals,users)
  });



  socket.on("leave",(data) => {
    handleLeave(data,activeGames,io)
 
  })

  socket.on("getWinners", () => {
    socket.emit("winners", winners);
  });

  socket.on("disconnect", () => {
    handleDisconnect(socket,activeGames,users,gameIntervals)
   
  });
});

app.use(express.static(path.join(__dirname, './build')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, './build', 'index.html'));
});

const PORT = process.env.SERVER_PORT
const IP = ip.address();
server.listen(PORT, () => console.log(`Server running on port ${PORT} and IP ${IP}`));



