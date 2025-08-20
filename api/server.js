// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./helpers/ball');
const { checkBingo, markPlayerCard } = require('./helpers/bingo');
const { handleJoin } = require('./helpers/handleJoin');
const { getWaitingGames } = require('./helpers/getWaitingGames');
const { clearGameIntervals } = require('./helpers/handleClearGameIntervals');
const { startCountDown } = require('./helpers/handleStartCountDown');
const { endGame } = require('./helpers/endGame');
const { handleLeave } = require('./helpers/handleLeave');
const { checkSingleCardBingo } = require('./helpers/singleBingo');
const { createGame } = require('./helpers/handleCreateGame');
const {handleBingo} = require('./helpers/handleBingo');
const { handleRefresh } = require('./helpers/handleRefresh');
const { handleDisconnect } = require('./helpers/handleDisconnect');
const { handlePlayerConnection } = require('./helpers/handlePlayerConnection');
const usersRouter = require('./routes/users');

const ip = require('ip');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
app.use(cors());
app.use(express.json()); // Add JSON body parsing middleware
app.use('/api/v1/users', usersRouter);
const server = http.createServer(app);



const io = socketIo(server, {
  cors: {
    origin: "*",
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
  socket.on("playerJoined", (data) => handlePlayerConnection(socket,data,activeGames))

  
  const waitingGames = getWaitingGames(activeGames, "waiting");
  const inProgressGames = getWaitingGames(activeGames, "in-progress");
  socket.emit("waitingGames", [...waitingGames, ...inProgressGames]);

  socket.on("handleRefresh",(data)=>handleRefresh(data,activeGames,io))
  


  socket.emit("waitingGames", waitingGames);
  socket.on("joinGame", (data) => {
    handleJoin(io,socket,data,activeGames,users,gameIntervals)
  });
  
  socket.on("bingo", (data) => {
    console.log("bingo", data)
    handleBingo(data,activeGames,io,gameIntervals,users)
  });



  socket.on("leave",(data) => {
    handleLeave(data,activeGames,io)
 
  })


  socket.on("playerLeft",(data) => {
    handlePlayerLeft(data,activeGames,io)
  })



  socket.on("getWinners", () => {
    socket.emit("winners", winners);
  });

  socket.on("disconnect", () => {
    handleDisconnect(io,socket,activeGames,users,gameIntervals)
   
  });
});


// const PORT = process.env.SERVER_PORT || 5000
const PORT = 5000 
const IP = ip.address();
server.listen(PORT, () => console.log(`Server running on port ${PORT} and IP ${IP}`));



