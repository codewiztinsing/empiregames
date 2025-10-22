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
    gameSpeed: 4000,
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
    disconnectedPlayers: new Map(),
    fauldMadePlayers: new Map(),
    // Fake picks during countdown (do not create real players)
    fakePickedNumbers: new Set(),
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
  game.fauldMadePlayers.clear();

  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) users.delete(socketId);
  }

  const data = await updateLastGame(game.roomId);
  startCountDown(game);

  io.emit("gameStatus", {
    status: "waiting",
    roomId: game.roomId,
    gameId: game.id
  });
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
        players: game.players ? game.players.size : 0,
        status: game.status
      });
    }
  }
  return waitingGames;
}

function startCountDown(game) {
  console.log("🚀 Starting countdown for game:", game.id, "with", game.players.size, "players");
  
  if (game.isCountStart || !game.players || game.players.size < 2) {
    console.log("❌ Cannot start countdown - isCountStart:", game.isCountStart, "players:", game.players?.size);
    return;
  }
  clearGameIntervals(game.id);
  game.countDown = 30; // Always reset to 30 when starting countdown
  game.isCountStart = true;
  console.log("⏰ Countdown started for game:", game.id, "countdown:", game.countDown);

  const countdownInterval = setInterval(() => {
    console.log("⏱️ Countdown tick - game:", game.id, "countdown:", game.countDown, "players:", game.players.size);
    
    // Check if we still have at least 2 players during countdown
    if (game.players.size < 2) {
      console.log("🔄 Less than 2 players during countdown - resetting countdown");
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.countDown = 30;
      game.status = "waiting";
      
      // Emit updated game state
        const displayTotalReset2 = (game.selectedNumbers.filter(num => num !== null).length) + (game.fakePickedNumbers ? game.fakePickedNumbers.size : 0);
        const displayWinReset2 = displayTotalReset2 * game.roomId * 0.78;

        io.emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: { numbers: game.selectedNumbers.filter(num => num !== null), fake: Array.from(game.fakePickedNumbers || []) },
          total_players: displayTotalReset2,
          win_amount: displayWinReset2,
        game_status: game.status,
        count_down: game.countDown
      });
      
      io.emit("globals", {
        roomId: game.roomId,
        countDown: game.countDown
      });
      
      return;
    }

    // Emit only real player selections plus fake picks for visual effect
    const realPicks = game.selectedNumbers.filter(num => num !== null);
    let fakePicksSnapshot = [];
    // Each tick, generate a few fake picks (1-3) unique in 1..400 for display only
    try {
      const maxFakePerTick = 3;
      const howMany = Math.min(maxFakePerTick, 3);
      if (!game.fakePickedNumbers) game.fakePickedNumbers = new Set();
      // decay fake picks over time to avoid indefinite growth
      if (game.fakePickedNumbers.size > 100) game.fakePickedNumbers.clear();
      const used = new Set([...realPicks, ...game.fakePickedNumbers]);
      for (let k = 0; k < howMany; k++) {
        let pick = Math.floor(Math.random() * 400) + 1;
        let attempts = 0;
        while (used.has(pick) && attempts < 500) {
          pick = Math.floor(Math.random() * 400) + 1;
          attempts++;
        }
        used.add(pick);
        game.fakePickedNumbers.add(pick);
      }
      fakePicksSnapshot = Array.from(game.fakePickedNumbers);
    } catch (e) {}

    const displayTotal = (realPicks?.length || 0) + (fakePicksSnapshot?.length || 0);
    const displayWin = displayTotal * game.roomId * 0.78;

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: { numbers: realPicks, fake: fakePicksSnapshot },
      total_players: 100,
      win_amount: 1000,
      game_status: game.status,
      count_down: game.countDown
    });

    io.emit("globals", {
      roomId: game.roomId,
      countDown: game.countDown
    })
  

  

    if (game.countDown === 0) {
      // Final check before starting game - ensure we have at least 2 players
      if (game.players.size < 2) {
        console.log("❌ Not enough players to start game - resetting countdown");
        clearInterval(countdownInterval);
        game.isCountStart = false;
        game.countDown = 30;
        game.status = "waiting";
        
        const displayTotalReset = (game.selectedNumbers.filter(num => num !== null).length) + (game.fakePickedNumbers ? game.fakePickedNumbers.size : 0);
        const displayWinReset = displayTotalReset * game.roomId * 0.78;

        io.emit("gameState", {
          gameId: game.id,
          roomId: game.roomId,
          pickedNumbers: { numbers: game.selectedNumbers.filter(num => num !== null), fake: Array.from(game.fakePickedNumbers || []) },
          total_players: displayTotalReset,
          win_amount: displayWinReset,
          game_status: game.status,
          count_down: game.countDown
        });
        
        io.emit("globals", {
          roomId: game.roomId,
          countDown: game.countDown
        });
        
        return;
      }
      
      console.log("🎮 Countdown reached 0 - starting game with", game.players.size, "players");
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.status = "in-progress"; // ✅ FIX: Set status to in-progress, not waiting
      game.countDown = 30; // Reset countdown for next game
      game.currentCall = null;
      game.calledNumbers = [];
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== null);
      game.win_amount = game.roomId * game.players.size * 0.78
      game.total_players = game.players.size
      startGame(game);
    }
    game.countDown--;
  }, 1000);
 
  gameIntervals.set(game.id, [countdownInterval]);
}

async function startGame(game) {
  console.log("🎮 Starting game for room:", game.roomId, "with", game.players.size, "players");
  game.status = "in-progress";
  clearGameIntervals(game.id);


   const playersWithSelectedNumbers = Array.from(game.players.entries()).map(([playerId, boards], idx) => {
    // Try to find the selected number for this player
    // game.selectedNumbersToPlayer is a Map<playerId, selectedNumber>
    let selectedNumber = null;
    if (game.selectedNumbersToPlayer && typeof game.selectedNumbersToPlayer.get === "function") {
      selectedNumber = game.selectedNumbersToPlayer.get(playerId) || null;
    }
    return {
      playerId,
      selectedNumber
    };
  });

  io.emit("gameStatus",{
    status: "in-progress",
    roomId: game.roomId
  })

  const players = Array.from(game.players.keys()).map(playerId => ({
    playerId: playerId,
    numberOfBoards: 1
  }));

  game.total_players = game.players.size
  game.total_winAmount = game.selectedNumbers.length * game.roomId * 0.78

  try {
    await gameLossWallet(players, game.id, game.total_players);
  } catch (error) {
    console.error('Error charging players:', error);
  }

  console.log("playersWithSelectedNumbers = ",playersWithSelectedNumbers)

 

  const emitNextBall = () => {
    console.log("🎲 Generating ball for game:", game.id, "called numbers:", game.calledNumbers.length);
    const calledSet = new Set(game.calledNumbers.map(b => b.number));
    let ball = generateBalls();
    while (calledSet.has(ball.number)) {
      ball = generateBalls();
    }
    game.currentCall = ball;
    game.calledNumbers.push(ball);
    game.selectedNumbers = [];
    console.log("🎯 Called ball:", ball.combined, "total called:", game.calledNumbers.length);
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.win_amount + (game.fakePickedNumbers ? game.fakePickedNumbers.size * game.roomId * 0.78 : 0),
      total_players: game.total_players + (game.fakePickedNumbers ? game.fakePickedNumbers.size : 0),
      lastBall: ball,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length,
      playersWithSelectedNumbers:playersWithSelectedNumbers

    });

    if (game.calledNumbers.length >= 75) {
      io.emit("gameStatus", {
        status: "waiting",
        roomId: game.roomId
      })
      endGame(game);
    }
  };

  // Emit the first ball immediately when the game starts (do not wait for gameSpeed)
  emitNextBall();

  // Subsequent balls follow the configured game speed
  const gameInterval = setInterval(emitNextBall, game.gameSpeed);

  gameIntervals.set(game.id, [gameInterval]);
}


function handleRefresh(data){
  console.log("handleRefresh", data)
  const game = activeGames.get(data.gameId);
  if (!game) return;
  io.emit("gameState", {
    gameId: game.id,
    roomId: game.roomId,
    total_players: game.total_players,
    pickedNumbers: game.selectedNumbers,
    game_status: game.status,
    count_down: game.countDown,
    win_amount: game.total_winAmount,
    lastBall: game.currentCall,
    called_numbers: game.calledNumbers,
    total_called_numbers: game.calledNumbers.length,
    total_players: game.total_players
  });

}


io.on('connection', (socket) => {
  socket.on("playerJoined", async (data) => {
    let game = activeGames.get(data.roomId);
    if (!game) {
      game = await createGame(data.roomId);
      activeGames.set(data.roomId, game);
    }
    const inProgressGames = [...activeGames.values()].filter(g => g.status === 'in-progress');
    socket.emit("activeGames", { activeGames: inProgressGames });
    socket.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
    socket.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown
    });

  // Send all player IDs and their selected numbers for in-progress games

    const playerSelections = [];
    for (const [playerId, numbers] of game.selectedNumbersToPlayer.entries()) {
      playerSelections.push({
        playerId,
        selectedNumbers: numbers
      });
    }
    
    console.log("📤 Emitting allPlayerSelections to player:", data.playerId);
    console.log("📤 Player selections data:", playerSelections);
    
    socket.emit("allPlayerSelections", {
      players: playerSelections,
      game_status: game.status
    });

 
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

    
    game.selectedNumbersToPlayer.set(data.playerId, [data.selectedNumber, data.selectedNumber2])


    game.numberOfBoardsToPlayer.set(data.playerId,data.numberOfBoards)
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
    if (game.players && game.players.size >= 100) {
      socket.emit('joinError', {
        message: 'Room is full (max 100 players).'
      });
      return;
    }

    const total_players = game.selectedNumbers.filter(num => num !== null).length

    const win_amount = total_players * game.roomId * 0.78
    game.total_winAmount = win_amount
    game.total_players = total_players


    // socket.join(data.roomId);

    const boards = [data.selectBoard];
    if (data.selectBoard2) {
      boards.push(data.selectBoard2);
    }
    game.players.set(data.playerId, boards);

  
  
    const playersList = [...game.players.keys()];
    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.total_players,
      game_status: game.status,
      count_down: game.countDown,
      players: playersList,
  
    });

    if (!game.isCountStart && game.players && game.players.size >= 2) {
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
    // If player previously made a false bingo, ignore further bingo attempts
    const gameForFaulCheck = activeGames.get(data.gameId);
    if (gameForFaulCheck && gameForFaulCheck.fauldMadePlayers && gameForFaulCheck.fauldMadePlayers.get && gameForFaulCheck.fauldMadePlayers.get(data.playerId) === true) {
      console.log("🚫 Ignoring bingo from disqualified player due to faul:", data.playerId);
      socket.emit("disqualified", { message: "You are disqualified for this round due to false bingo.", roomId: data.roomId, gameId: data.gameId });
      return;
    }

    const game = activeGames.get(data.gameId);
    if (!game || game.status !== 'in-progress') return;
    const playerCards = game.players.get(data.playerId);
    if (!playerCards || !Array.isArray(playerCards)) return;
    const board = data.board
    const boardNumber = data.boardNumber
    const markedSingleCard = markPlayerCard(board, game.calledNumbers)
    const isSingleBingo = checkSingleCardBingo(markedSingleCard)
    if(isSingleBingo){
      io.emit("winBingo", {
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

    io.emit("bingoWinner", {
        isBingo: true,
        playerId: data.playerId,
        markedCells: markedSingleCard,
        winningCard: markedSingleCard,
        winner: data.playerId,
        winnerCardNumber: boardNumber,
        winnerPlayerName: data.playerName,
        winningCard: markedSingleCard,
        gameId: data.gameId,
        roomId: data.roomId
      })

      try {
        const response = await gameWinWallet(
          data.playerId,
          game.roomId,
          game.win_amount,
          game.total_players
        );
      } catch (error) {
        console.error("Error processing win wallet:", error);
      }

      endGame(game);
    }

    else{
      game.fauldMadePlayers.set(data.playerId, true);
      io.emit("falseBingo", {
        isBingo: false,
        playerId: data.playerId,
        losser_board: boardNumber,
      })
    }
      

  
    
});
  

socket.on("faulMadePlayer", (data) => {
  const game = Array.from(activeGames.values()).find(g => g.status === 'in-progress' && g.id === data.gameId);
  
  if (!game) {
    console.log("❌ Game not found for faulMadePlayer event");
    return;
  }

  // Gather all players who have made a faul (false bingo)
  const faulPlayers = [];
  for (const [playerId, value] of game.fauldMadePlayers.entries()) {
    if (value) {
      faulPlayers.push(playerId);
    }
  }

  io.emit("faulMadePlayers", {
    gameId: data.gameId,
    roomId: game.roomId,
    faulPlayers: faulPlayers
  });
})


  socket.on("leave",(data) => {
  
    
    const game = activeGames.get(data.roomId);
    if (!game) {
      console.log("❌ ERROR: Game not found for roomId:", data.roomId);
      return;
    }
    
    console.log("Game found:", {
      id: game.id,
      status: game.status,
      roomId: game.roomId
    });
  
    const playerId = data.playerId
    const selectedNumber = data.selectedNumber
    const selectedNumber2 = data.selectedNumber2 || null // Handle case where selectedNumber2 might not be provided
    
    // If game is in progress, preserve player data for potential reconnection
    if (game.status === 'in-progress') {
      console.log("🔄 Game is in progress - preserving player data for reconnection");
      // Store player's game state for reconnection
      if (!game.disconnectedPlayers) {
        game.disconnectedPlayers = new Map();
      }
      
      const playerData = {
        playerId: playerId,
        selectedNumber: selectedNumber,
        selectedNumber2: selectedNumber2,
        boards: game.players.get(playerId),
        numberOfBoards: game.numberOfBoardsToPlayer.get(playerId),
        markedCells: data.markedCells || [],
        disconnectedAt: Date.now()
      };
      
      console.log("💾 Storing player data:", {
        playerId: playerData.playerId,
        selectedNumber: playerData.selectedNumber,
        hasBoards: !!playerData.boards,
        markedCells: playerData.markedCells.length,
        disconnectedAt: new Date(playerData.disconnectedAt).toISOString()
      });
      
      game.disconnectedPlayers.set(playerId, playerData);

      // Mark player as disqualified for the current round upon leaving mid-game
      try {
        if (!game.fauldMadePlayers) {
          game.fauldMadePlayers = new Map();
        }
        game.fauldMadePlayers.set(playerId, true);

        // Broadcast disqualification and the updated list of disqualified (faul) players
        const faulPlayers = [];
        for (const [pid, val] of game.fauldMadePlayers.entries()) {
          if (val) faulPlayers.push(pid);
        }

        io.emit("disqualified", {
          message: "You left during an active game. You are disqualified for this round.",
          roomId: game.roomId,
          gameId: game.id,
          playerId: playerId
        });

        io.emit("faulMadePlayers", {
          gameId: game.id,
          roomId: game.roomId,
          faulPlayers
        });
      } catch (e) {
        console.log("Error marking player disqualified on leave:", e);
      }
   
      
      // Immediate verification
      const storedData = game.disconnectedPlayers.get(playerId);
      if (storedData) {
        console.log("✅ Immediate verification successful xxxxxxxxx- data exists");
      } else {
        console.log("❌ Immediate verification failed - data not found!");
      }
      
      // Remove from active players but keep in selectedNumbers for game continuity
      if (game?.players?.has(playerId)) {
        game.players.delete(playerId);
      }
      
      // Don't remove from selectedNumbers for in-progress games
      // This allows the game to continue with the same player count
      
    } else {
      console.log("⏳ Game is waiting - removing player completely");
      // For waiting games, remove completely as before
      if (game?.players?.has(playerId)) {
        game.players.delete(playerId);
        console.log("🗑️ Removed player from active players");
      }
      
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber);
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber2);
      game.selectedNumbersToPlayer.delete(playerId)
      game.selectedNumbersToPlayer.delete(playerId)
    }
    

    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      total_players: game.selectedNumbers.length,
      game_status: game.status,
    })
  
    io.emit("waitingGames",   [...getWaitingGames(activeGames),...getWaitingGames(activeGames,"waiting")]);

    io.emit("playerLeft",{
      playerId: data.playerId,
      selectedNumber: data.selectedNumber,
      selectedNumber2: data.selectedNumber2
    })

    // Check if countdown is running and we have less than 2 players
    if (game.isCountStart && game.players.size < 2) {
      console.log("🔄 Less than 2 players during countdown - resetting countdown from 30");
      clearGameIntervals(game.id);
      game.isCountStart = false;
      game.countDown = 30;
      game.status = "waiting";
      
      // Emit updated game state
      io.emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: game.selectedNumbers,
        total_players: game.selectedNumbers.length,
        game_status: game.status,
        count_down: game.countDown
      });
      
      // Only start countdown if we have at least 2 players
      if (game.players.size >= 2) {
        startCountDown(game);
      }
    }
    
  })


  socket.on("getWinners", () => {
    socket.emit("winners", winners);
  });

  socket.on("getAllPlayerSelections", (data) => {
    console.log("📥 Received getAllPlayerSelections request from player:", data.playerId);
    const game = activeGames.get(data.roomId);
    if (!game) {
      console.log("❌ Game not found for getAllPlayerSelections");
      return;
    }

    const playerSelections = [];
    for (const [playerId, numbers] of game.selectedNumbersToPlayer.entries()) {
      playerSelections.push({
        playerId,
        selectedNumbers: numbers
      });
    }
    
    console.log("📤 Sending allPlayerSelections to requesting player:", data.playerId);
    console.log("📤 Player selections data:", playerSelections);
    console.log("📤 Game status:", game.status);
    
    socket.emit("allPlayerSelections", {
      players: playerSelections,
      game_status: game.status
    });
  });

  // Rejoin logic removed

  socket.on("disconnect", () => {
   
    const user = users.get(socket.id);
    if (user) {
      const game = activeGames.get(user.gameId);
      const playerId = user.playerId
   
      if(game.selectedNumbersToPlayer.has(playerId)){
        const selectedNumber = game.selectedNumbersToPlayer.get(playerId)[0]
        const selectedNumber2 = game.selectedNumbersToPlayer.get(playerId)[1]
        game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber);
        game.selectedNumbers = game.selectedNumbers.filter(num => num !== selectedNumber2);
      }
     
 
      if (game?.players.has(user.playerId)) {
        let selectedNumber = null;
        let selectedNumber2 = null;
        
        if(game.selectedNumbersToPlayer.has(playerId)){
          selectedNumber = game.selectedNumbersToPlayer.get(playerId)[0]
          selectedNumber2 = game.selectedNumbersToPlayer.get(playerId)[1]
        }
        
        if(game.status === "waiting") {
          // For waiting games, remove player completely
          game.players.delete(user.playerId);
          
          if (selectedNumber) {
            game.selectedNumbers = game?.selectedNumbers?.filter(num => num !== selectedNumber);
          }
          if (selectedNumber2) {
            game.selectedNumbers = game?.selectedNumbers?.filter(num => num !== selectedNumber2);
          }
    
          io.emit("gameState", {
            message: `User ${user.playerId} disconnected`,
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers.filter(num => {
              if (selectedNumber && num === selectedNumber) return false;
              if (selectedNumber2 && num === selectedNumber2) return false;
              return true;
            }),
            total_players: game.selectedNumbers.length,
            game_status: game.status,
            count_down: game.countDown
          });

          game.selectedNumbersToPlayer.delete(playerId)
          io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
          users.delete(socket.id);

          // Check if countdown is running and we have less than 2 players
          if (game.isCountStart && game.players.size < 2) {
            console.log("🔄 Less than 2 players during countdown - resetting countdown from 30");
            clearGameIntervals(game.id);
            game.isCountStart = false;
            game.countDown = 30;
            game.status = "waiting";
            
            // Emit updated game state
            io.emit("gameState", {
              gameId: game.id,
              roomId: game.roomId,
              pickedNumbers: game.selectedNumbers,
              total_players: game.selectedNumbers.length,
              game_status: game.status,
              count_down: game.countDown
            });
            
            // Only start countdown if we have at least 2 players
            if (game.players.size >= 2) {
              startCountDown(game);
            }
          }
        } else if(game.status === "in-progress") {
          // On disconnect during in-progress, simply remove active mapping without rejoin tracking
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

const PORT = process.env.PORT || 5000
const IP = ip.address();
server.listen(PORT, () => console.log(`Server running on port ${PORT} and IP ${IP}`));



