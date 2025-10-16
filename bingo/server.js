// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { checkSingleCardBingo } = require('./src/helpers/singleBingo');
const { gameWinWallet,gameLossWallet,updateLastGame,getGameSettings, updateGameMetrics } = require('./api');
const ip = require('ip');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
app.use(cors());
const server = http.createServer(app);


const getConstant = async () => {
  return {
    gameSpeed: 3000,
    countDown: 5
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

// ---------------- Utility helpers (non-breaking) ----------------
const { computeTotals, emitGameState } = require('./src/helpers/serverHelpers');

// Ethiopian fake user names (first and last) for realistic winner announcements
const ETH_FIRST_NAMES = [
  'Abebe','Kebede','Haile','Bekele','Mulu','Tesfaye','Meron','Saba','Marta','Hanna','Mulugeta','Alemu','Lulit','Lidya','Yohannes','Dereje','Samrawit','Saron','Mahider','Hirut','Eden','Yared','Nati','Miki','Tigist','Aida','Rahel','Yetnayet','Mekdes','Eyerusalem','Nahom','Henok','Daniel','Fikirte','Blen','Rediet','Bethelhem','Selam','Selamawit','Abel','Samuel','Mersha','Fitsum','Gashaw','Girma','Solomon','Mebratu','Genet','Lensa','Fanaye','Mahi','Sosina','Tsion','Kidus','Kaleb','Abraham','Mikiyas','Biruk','Natnael','Yonatan','Yonas','Marta','Ruth','Mimi','Yemisrach','Yeshi','Seble','Hiwot','Mignot','Sosena','Mahlet','Mahi','Lensa','Lensa','Saron','Feven','Bethel','Hermela','Mikias','Nebiyu','Brook','Surafel','Senait','Abush','Fitsum','Asnakech','Azeb','Hanan','Hawi','Hewan','Bethelhem','Tsige','Mebrahtu','Kidist','Eleni','Lulit','Medhanit','Tinsae','Edom','Sosina','Eyerus','Netsanet','Selamnesh','Hayat','Zemzem','Feysel','Sami','Jafar','Hamdi'
];
const ETH_LAST_NAMES = [
  'Tesfaye','Bekele','Alemu','Wondimu','Gebremedhin','Gebremariam','Gebrehiwot','Gebru','Gebre','Gebreyesus','Gebremichael','Hailemariam','Haile','Hailu','Kassahun','Kassaye','Fekadu','Asfaw','Tadesse','Tsegaye','Tefera','Girma','Gebremariam','Demissie','Yohannes','Solomon','Worku','Alemayehu','Gebrekidan','Gebretsadik','Kebede','Abate','Abera','Abraham','Admasu','Adugna','Assefa','Ayalew','Ayana','Bekri','Belay','Belayneh','Berhane','Berhanu','Berhe','Beyene','Biniam','Birhanu','Biruk','Bogale','Buzuayehu','Dagnachew','Dawit','Desalegn','Desale','Diriba','Ephrem','Eshetu','Fisseha','Gebrekirstos','Geda','Getachew','Gizaw','Habtamu','Hagos','Haileselassie','Hassen','Hiruy','Kidane','Kidanemariam','Kifle','Kiros','Legesse','Lemi','Mamo','Mebratu','Mehari','Mehari','Melaku','Melese','Mengistu','Merga','Mersha','Michael','Moges','Molla','Nigussie','Reda','Sahle','Seyoum','Shiferaw','Sime','Tafese','Tariku','Tekeste','Tekle','Terefe','Tesfamariam','Tesfatsion','Tessema','Weldeyesus','Woldemariam','Woldemichael','Woldeselassie','Wondafrash','Yared','Yesuf','Yimer','Zewdu'
];

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
    roomId,
    fakeWinnerScheduled: false,
    fakeSelectionActive: false,
    fakeTargetCount: 0
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
  game.fakeWinnerScheduled = false;

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
 
  if (game.isCountStart || !game.players || game.players.size < 1) return;
  clearGameIntervals(game.id);
  game.countDown = 30; // Always reset to 30 when starting countdown
  game.isCountStart = true;

  const countdownInterval = setInterval(() => {
    // Check if we still have at least 1 player during countdown
    if (game.players.size < 1) {
      console.log("🔄 Less than 2 players during countdown - resetting countdown");
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.countDown = 30;
      game.status = "waiting";
      
      // Emit updated game state
      io.emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        game_status: game.status,
        count_down: game.countDown
      });
      
     
      return;
    }



     // Broadcast fake selections while waiting: target random 30..50 unique numbers
     if (game.status === 'waiting') {
      if (!game.fakeSelectionActive) {
        game.fakeSelectionActive = true;
        game.fakeTargetCount = 30 + Math.floor(Math.random() * 21); // 30..50
        console.log(`[FAKE_SIM] INIT room=${game.roomId} gameId=${game.id} target=${game.fakeTargetCount}`);
      }
      const cap = Math.max(30, Math.min(50, game.fakeTargetCount || 30));
      const current = game.selectedNumbers.filter(n => n !== null).length;
      console.log(`[FAKE_SIM] STATE room=${game.roomId} gameId=${game.id} current=${current} cap=${cap}`);
      if (current < cap) {
        const universe = Array.from({ length: 400 }, (_, i) => i + 1);
        const taken = new Set(game.selectedNumbers.filter(n => n !== null));
        const candidates = universe.filter(n => !taken.has(n));
        console.log(`[FAKE_SIM] CAND room=${game.roomId} gameId=${game.id} candidates=${candidates.length}`);
        if (candidates.length > 0) {
          const missing = Math.min(cap - current, Math.min(3, candidates.length));
          const chosenList = [];
          for (let i = 0; i < missing; i++) {
            const idx = Math.floor(Math.random() * candidates.length);
            const chosen = candidates.splice(idx, 1)[0];
            game.selectedNumbers.push(chosen);
            chosenList.push(chosen);
          }
          console.log(`[FAKE_SIM] ADD room=${game.roomId} gameId=${game.id} chosen=${JSON.stringify(chosenList)} total=${game.selectedNumbers.filter(n=>n!==null).length}`);
          io.emit('pickedNumbers', { roomId: game.roomId, numbers: game.selectedNumbers });
          console.log(`[FAKE_SIM] EMIT pickedNumbers room=${game.roomId} count=${game.selectedNumbers.length}`);
          // Totals and consolidated gameState will be emitted below once per tick
        }
      }
    } else {
      // Reset fake selection flags once game progresses
      if (game.fakeSelectionActive) {
        console.log(`[FAKE_SIM] RESET room=${game.roomId} gameId=${game.id}`);
      }
      game.fakeSelectionActive = false;
      game.fakeTargetCount = 0;
    }
    // Compute totals (including fake selections) for broadcast
    const broadcastSelected = game.selectedNumbers.filter(num => num !== null);
    const broadcastTotalPlayers = broadcastSelected.length;
    const broadcastWinAmount = broadcastTotalPlayers * game.roomId * 0.78;
    game.total_players = broadcastTotalPlayers;
    game.total_winAmount = broadcastWinAmount;

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: broadcastSelected,
      total_players: broadcastTotalPlayers,
      win_amount: broadcastWinAmount,
      game_status: game.status,
      count_down: game.countDown
    });

  
  

  

    if (game.countDown === 0) {
      // Final check before starting game - ensure we have at least 1 player
      if (game.players.size < 1) {
        console.log("❌ Not enough players to start game - resetting countdown");
        clearInterval(countdownInterval);
        game.isCountStart = false;
        game.countDown = 30;
        game.status = "waiting";
        
        io.emit("gameState", {
          gameId: game.id,
          roomId: game.roomId,
          pickedNumbers: game.selectedNumbers.filter(num => num !== null),
          total_players: game.selectedNumbers.filter(num => num !== null).length,
          
          game_status: game.status,
          count_down: game.countDown
        });
        
      
        
        return;
      }
      
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.status = "waiting";
      game.countDown = 30; // Reset countdown for next game
      game.currentCall = null;
      game.calledNumbers = [];
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== null);

      // Freeze metrics at start (include fakes)
      const realPlayersAtStart = game.players ? game.players.size : 0;
      const totalPlayersAtStart = game.selectedNumbers.length;
      const fakePlayersAtStart = Math.max(0, totalPlayersAtStart - realPlayersAtStart);
      const winAmountAtStart = totalPlayersAtStart * game.roomId * 0.78;

      game.total_players = totalPlayersAtStart;
      game.total_winAmount = winAmountAtStart;
      game.win_amount = winAmountAtStart;

     
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
    roomId: game.roomId,
    game_status: "in-progress"
  })

  const players = Array.from(game.players.keys()).map(playerId => ({
    playerId: playerId,
    numberOfBoards: 1
  }));

  game.total_players = game.players.size
  game.total_winAmount = game.selectedNumbers.length * game.roomId * 0.78

  try {
    await gameLossWallet(players, game.id, game.total_players, game.fake_players);
    
    // Calculate number of fake players (assuming fake players fill up to 50 total, rest are real)
    const maxPlayers = 50;
    const realPlayers = game.total_players;
    const fakePlayers = Math.max(0, maxPlayers - realPlayers);
    game.fake_players = fakePlayers;

    updateGameMetrics(game.roomId, realPlayers, fakePlayers, realPlayers, game.total_winAmount);

  } catch (error) {
    console.error('Error charging players:', error);
  }

  console.log("playersWithSelectedNumbers = ",playersWithSelectedNumbers)

 

  const gameInterval = setInterval(async () => {
    const calledSet = new Set(game.calledNumbers.map(b => b.number));
    let ball = generateBalls();
    while (calledSet.has(ball.number)) {
      ball = generateBalls();
    }
    game.currentCall = ball;
    game.calledNumbers.push(ball);
    game.selectedNumbers = [];
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  
    // Schedule a fake winner once at least 10 numbers have been called
    if (!game.fakeWinnerScheduled && game.calledNumbers.length >= 20) {
      await scheduleFakeWinner(game);
    }

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.win_amount,
      total_players: Math.max(30, 50),
      lastBall: ball,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length,
      playersWithSelectedNumbers:playersWithSelectedNumbers

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

function generateFakeWinningCard() {
  // Create a 5x5 card structure similar to client expectations with marked cells
  const ranges = [
    [1, 15], [16, 30], [31, 45], [46, 60], [61, 75]
  ];
  // Build base grid (rows x cols), then transpose to match client structure [col][row]
  const base = Array.from({ length: 5 }, () => Array(5).fill(null));
  for (let col = 0; col < 5; col++) {
    const nums = [];
    for (let n = ranges[col][0]; n <= ranges[col][1]; n++) nums.push(n);
    for (let row = 0; row < 5; row++) {
      const idx = Math.floor(Math.random() * nums.length);
      const num = nums.splice(idx, 1)[0];
      base[row][col] = { number: row === 2 && col === 2 ? '*' : num, marked: false };
    }
  }
  const grid = base[0].map((_, colIndex) => base.map(row => row[colIndex]));

  // Choose a random winning pattern
  const patterns = ['row', 'col', 'diag', 'anti', 'fourCorners', 'fourEdges'];
  const pick = patterns[Math.floor(Math.random() * patterns.length)];

  if (pick === 'row') {
    const r = Math.floor(Math.random() * 5);
    for (let c = 0; c < 5; c++) grid[c][r].marked = true;
  } else if (pick === 'col') {
    const c = Math.floor(Math.random() * 5);
    for (let r = 0; r < 5; r++) grid[c][r].marked = true;
  } else if (pick === 'diag') {
    for (let i = 0; i < 5; i++) grid[i][i].marked = true;
  } else if (pick === 'anti') {
    for (let i = 0; i < 5; i++) grid[4 - i][i].marked = true;
  } else if (pick === 'fourCorners') {
    grid[0][0].marked = true;
    grid[0][4].marked = true;
    grid[4][0].marked = true;
    grid[4][4].marked = true;
  } else if (pick === 'fourEdges') {
    // Cross-like edges as per client check
    grid[2][0].marked = true;
    grid[0][2].marked = true;
    grid[2][4].marked = true;
    grid[4][2].marked = true;
  }

  // Ensure center is marked for patterns that commonly include it
  grid[2][2].marked = true;

  return grid;
}

async function scheduleFakeWinner(game) {
  console.log("scheduleFakeWinner calledNumbers.length = ", game.calledNumbers.length)
  try {
    game.fakeWinnerScheduled = true;
    const delayMs = 5000 + Math.floor(Math.random() * 15000); // 5-20 seconds
    setTimeout(() => {
      try {
        // Only announce if game still running and no real winner has been processed
        if (!activeGames.has(game.id)) return;
        const g = activeGames.get(game.id);
        if (!g || g.status !== 'in-progress') return;

        const first = ETH_FIRST_NAMES[Math.floor(Math.random() * ETH_FIRST_NAMES.length)];
        const last = ETH_LAST_NAMES[Math.floor(Math.random() * ETH_LAST_NAMES.length)];
        const fakeName = `${first} ${last}`;
        const fakeCardNumber = 1 + Math.floor(Math.random() * 400);
        const winningCard = generateFakeWinningCard();

        io.emit("bingoWinner", {
          isBingo: true,
          playerId: 'BOT_FAKE',
          markedCells: winningCard,
          winningCard: winningCard,
          winner: 'BOT_FAKE',
          winnerCardNumber: fakeCardNumber,
          winnerPlayerName: fakeName,
          gameId: g.id,
          roomId: g.roomId
        });

        // Persist metrics at fakw win moment and mark backend ended
        try {
          const realPlayers = g.players ? g.players.size : 0;
          const totalPlayers = (g.selectedNumbers || []).filter(n => n !== null).length;
          const fakePlayers = Math.max(0, totalPlayers - realPlayers);
          const winAmount = totalPlayers * g.roomId * 0.78;
          g.total_players = totalPlayers;
          g.total_winAmount = winAmount;
          g.win_amount = winAmount;
          // Persist to backend and end last game (no wallet ops for fake winners)
          updateGameMetrics(g.roomId, realPlayers, fakePlayers, totalPlayers, winAmount);
          updateLastGame(g.roomId);
          console.log(`[END_GAME][FAKE_WIN] room=${g.roomId} real=${realPlayers} fake=${fakePlayers} total=${totalPlayers} win=${winAmount}`);
        } catch (e) {
          console.log('[METRICS][FAKE_WIN] error', e?.message || e);
        }

      

        // End the game after announcing fake winner (no wallet ops for fake)
        endGame(g);
      } catch (err) {}
    }, delayMs);
  } catch (e) {}
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

    if (!game.isCountStart && game.players && game.players.size >= 1) {
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

    // Check if countdown is running and we have less than 1 player
    if (game.isCountStart && game.players.size < 1) {
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
      
      // Only start countdown if we have at least 1 player
      if (game.players.size >= 1) {
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

  // Handle game rejoin
  socket.on("rejoinGame", (data) => {
    console.log("🔄 Rejoin request from player:", data.playerId, "for room:", data.roomId);
    const game = activeGames.get(data.roomId);
    
    if (!game) {
      console.log("❌ Game not found for rejoin");
      socket.emit("rejoinError", { message: "Game not found" });
      return;
    }

    // Check if player has disconnected data
    if (!game.disconnectedPlayers || !game.disconnectedPlayers.has(data.playerId)) {
      console.log("❌ No rejoin data found for player:", data.playerId);
      socket.emit("rejoinError", { message: "No previous game data found" });
      return;
    }

    const playerData = game.disconnectedPlayers.get(data.playerId);
    console.log("✅ Found rejoin data for player:", playerData);

    // If player had made a false bingo (faul), disqualify and do not restore to active game
    const wasFaulMade = !!(game.fauldMadePlayers && game.fauldMadePlayers.get && game.fauldMadePlayers.get(data.playerId) === true);
    if (wasFaulMade) {
      console.log("🚫 Player is disqualified due to false bingo, not restoring:", data.playerId);
      socket.emit("rejoinError", { message: "You are disqualified for this round due to false bingo.", disqualified: true });
      // Still provide state snapshot so client can reflect current game without enabling actions
      socket.emit("rejoinSuccess", {
        playerId: data.playerId,
        gameId: game.id,
        roomId: game.roomId,
        selectedNumber: playerData.selectedNumber,
        selectedNumber2: playerData.selectedNumber2,
        boards: playerData.boards,
        markedCells: playerData.markedCells,
        calledNumbers: game.calledNumbers.map(ball => ball.number),
        lastBall: game.currentCall,
        totalCalledNumbers: game.calledNumbers.length,
        win_amount: game.win_amount,
        total_players: game.total_players,
        game_status: game.status,
        faulMade: true
      });
      return;
    }

    // Restore player to active game
    game.players.set(data.playerId, playerData.boards);
    game.numberOfBoardsToPlayer.set(data.playerId, playerData.numberOfBoards);
    game.selectedNumbersToPlayer.set(data.playerId, [playerData.selectedNumber]);
    
    // Remove from disconnected players
    game.disconnectedPlayers.delete(data.playerId);

    // Determine if this player had already made a false bingo (faul)
    const hasFaulMade = !!(game.fauldMadePlayers && game.fauldMadePlayers.get && game.fauldMadePlayers.get(data.playerId) === true);

    // Send rejoin success with current game state
    socket.emit("rejoinSuccess", {
      playerId: data.playerId,
      gameId: game.id,
      roomId: game.roomId,
      selectedNumber: playerData.selectedNumber,
      selectedNumber2: playerData.selectedNumber2,
      boards: playerData.boards,
      markedCells: playerData.markedCells,
      calledNumbers: game.calledNumbers.map(ball => ball.number),
      lastBall: game.currentCall,
      totalCalledNumbers: game.calledNumbers.length,
      win_amount: game.win_amount,
      total_players: game.total_players,
      game_status: game.status,
      faulMade: hasFaulMade
    });

    console.log("✅ Player successfully rejoined:", data.playerId);
  });

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
        if(game.status === "waiting") {
          game.players.delete(user.playerId);
          let selectedNumber = null;
          let selectedNumber2 = null;
          
          if(game.selectedNumbersToPlayer.has(playerId)){
            selectedNumber = game.selectedNumbersToPlayer.get(playerId)[0]
            selectedNumber2 = game.selectedNumbersToPlayer.get(playerId)[1]
          }
          
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
            count_down: game.countDown,
            total_players: game.total_players
          });


        
          game.selectedNumbersToPlayer.delete(playerId)
          game.selectedNumbersToPlayer.delete(playerId)
         
          io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
          users.delete(socket.id);
          users.delete(socket.id);
          users.delete(socket.id);

          // Check if countdown is running and we have less than 1 player
          if (game.isCountStart && game.players.size < 1) {
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
            
            // Only start countdown if we have at least 1 player
            if (game.players.size >= 1) {
              startCountDown(game);
            }
          }

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



