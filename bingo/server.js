// server.js
const express = require('express');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { generateBalls } = require('./src/helpers/ball');
const { checkBingo, markPlayerCard } = require('./src/helpers/bingo');
const { checkSingleCardBingo } = require('./src/helpers/singleBingo');
const { gameWinWallet,gameLossWallet,getGameSettings,getFakePlayerSettings } = require('./api');
const { generateFixedCard } = require('./src/helpers/serverFixedBingoCards');
const ip = require('ip');
const dotenv = require('dotenv');
dotenv.config();
const app = express();
app.use(cors());
const server = http.createServer(app);




const getConstant = async () => {
  return {
    gameSpeed: 1000,
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

// ---------------- Utility helpers (non-breaking) ----------------
const { computeTotals, emitGameState } = require('./src/helpers/serverHelpers');

// Promotion functions
function sendPromotionToAllPlayers(promotionData) {
  console.log('Sending promotion to all players:', promotionData);
  io.emit('promotion_received', {
    type: 'promotion',
    data: promotionData,
    timestamp: new Date().toISOString()
  });
}

// Expose promotion function globally for admin use
global.sendPromotionToAllPlayers = sendPromotionToAllPlayers;

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

// Periodically refresh fake-player settings so dashboard toggles apply to running games
async function refreshGameSettings(game) {
  try {
    const now = Date.now();
    if (!game.lastSettingsFetchAt || (now - game.lastSettingsFetchAt) > 10000) { // refresh every 10s
      console.log("refreshGameSettings - refreshing");
      const latest = await getConstant();
      if (latest && typeof latest.fake_players_can_win === 'boolean') {
        game.fakePlayersCanWin = latest.fake_players_can_win;
      }
      if (latest && typeof latest.calls_before_fake_winner === 'number') {
        game.callsBeforeFakeWinner = latest.calls_before_fake_winner;
      }
      if (latest && typeof latest.max_fake_players === 'number') {
        game.maxFakePlayers = latest.max_fake_players;
        console.log(`Updated maxFakePlayers to: ${game.maxFakePlayers}`);
      }
      game.lastSettingsFetchAt = now;
    }
  } catch (e) {
    console.error("Error refreshing game settings:", e);
  }
}

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
    fakeTargetCount: 0,
    // Dynamic fake player settings
    maxFakePlayers: gameSettings.max_fake_players,
    callsBeforeFakeWinner: gameSettings.calls_before_fake_winner,
    fakePlayersCanWin: gameSettings.fake_players_can_win,
    lastSettingsFetchAt: Date.now()
  };
  console.log(`=== CREATING NEW GAME ===`);
  console.log(`Game roomId: ${roomId}`);
  console.log(`Game ID: ${game.id}`);
  console.log(`Max Fake Players from API: ${gameSettings.max_fake_players}`);
  console.log(`Game maxFakePlayers: ${game.maxFakePlayers}`);
  console.log(`Game status: ${game.status}`);
  activeGames.set(roomId, game);
  console.log(`Game stored with key: ${roomId}`);
  console.log(`Total active games: ${activeGames.size}`);
  console.log(`Active games keys: ${Array.from(activeGames.keys())}`);
  console.log(`=== END CREATING GAME ===`);
  return game;
}




function clearGameIntervals(gameId) {
  if (gameIntervals.has(gameId)) {
    gameIntervals.get(gameId).forEach(clearInterval);
    gameIntervals.delete(gameId);
  }
}

function endGameDueToWinner(game) {
  // Mark game as ended due to winner
  game.gameOver = true;
  game.status = "completed";
  
  // Clear intervals to stop the game
  clearGameIntervals(game.id);
  
  // Emit game ended status
  io.emit("gameStatus", {
    status: "completed",
    roomId: game.roomId,
    gameId: game.id
  });
  
  // After a delay, reset the game for next round
  setTimeout(() => {
    endGame(game);
  }, 5000); // 5 second delay to show winner
}

async  function endGame(game) {
  clearGameIntervals(game.id);
  game.players.clear();
  game.calledNumbers = [];
  game.currentCall = null;
  game.status = "waiting";
  game.gameOver = false; // Reset for next game
  game.winner = null;
  game.countDown = game.countDown || 30;
  game.isCountStart = false;
  game.fauldMadePlayers.clear();
  game.fakeWinnerScheduled = false;
  game.fakeSelectionActive = false;
  game.fakeTargetCount = 0;

  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) users.delete(socketId);
  }

  // End the game in backend - no longer needed since we removed update-metrics endpoint
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
  game.countDown = game.countDown || 30; // Use game's countdown time or default to 30
  game.isCountStart = true;

  const countdownInterval = setInterval(async () => {
    // Check if we still have at least 1 player during countdown
    if (game.players.size < 1) {
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.countDown = game.countDown || 30;
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



     // Broadcast fake selections while waiting: use max fake players from API
     console.log(`Game status: ${game.status}, fakeSelectionActive: ${game.fakeSelectionActive}`);
     
     if (game.status === 'waiting') {
      if (!game.fakeSelectionActive) {
        game.fakeSelectionActive = true;
        // Generate random number of fake players for this game (between 30-80% of max)
        const maxFakePlayers = game.maxFakePlayers || 50;
        const minFakePlayers = Math.floor(maxFakePlayers * 0.3); // 30% of max
        const maxFakePlayersForGame = Math.floor(maxFakePlayers * 0.8); // 80% of max
        game.fakeTargetCount = Math.floor(Math.random() * (maxFakePlayersForGame - minFakePlayers + 1)) + minFakePlayers;
        console.log(`Starting fake selection with random target: ${game.fakeTargetCount} (range: ${minFakePlayers}-${maxFakePlayersForGame}, max: ${maxFakePlayers})`);
      }
      const cap = game.fakeTargetCount || game.maxFakePlayers || 50;
      const current = game.selectedNumbers.filter(n => n !== null).length;
      console.log(`Fake player selection: current=${current}, cap=${cap}, target=${game.fakeTargetCount}, maxFakePlayers=${game.maxFakePlayers}, gameStatus=${game.status}`);
      
      if (current < cap) {
        const universe = Array.from({ length: 800 }, (_, i) => i + 1);
        const taken = new Set(game.selectedNumbers.filter(n => n !== null));
        const candidates = universe.filter(n => !taken.has(n));
        console.log(`Available candidates: ${candidates.length}, taken: ${taken.size}`);
        
        if (candidates.length > 0) {
          // Human-like selection patterns with varying behavior
          let playersThisTick;
          
          // Simulate different player behaviors with occasional pauses
          const behaviorPattern = Math.random();
          const pauseChance = Math.random();
          
          // 10% chance of a pause (simulating players thinking or getting distracted)
          if (pauseChance < 0.1) {
            console.log(`Fake players taking a pause (simulating human behavior)`);
            const pauseDelay = Math.floor(Math.random() * 2000) + 500; // 500-2500ms pause
            await new Promise(resolve => setTimeout(resolve, pauseDelay));
            return; // Skip this tick
          }
          
          if (behaviorPattern < 0.25) {
            // Slow, thoughtful players (1 player per tick)
            playersThisTick = 1;
          } else if (behaviorPattern < 0.65) {
            // Normal players (1-2 players per tick)
            playersThisTick = Math.floor(Math.random() * 2) + 1;
          } else if (behaviorPattern < 0.9) {
            // Quick players (2-3 players per tick)
            playersThisTick = Math.floor(Math.random() * 2) + 2;
          } else {
            // Burst players (occasionally select 3-4 players quickly)
            playersThisTick = Math.floor(Math.random() * 2) + 3;
          }
          
          const maxPerTick = Math.min(4, cap - current);
          playersThisTick = Math.min(playersThisTick, maxPerTick);
          const missing = Math.min(playersThisTick, candidates.length);
          
          console.log(`Selecting ${missing} fake players (behavior: ${behaviorPattern.toFixed(2)}, pause: ${pauseChance.toFixed(2)})`);
          
          const chosenList = [];
          for (let i = 0; i < missing; i++) {
            const idx = Math.floor(Math.random() * candidates.length);
            const chosen = candidates.splice(idx, 1)[0];
            game.selectedNumbers.push(chosen);
            chosenList.push(chosen);
            
            // Simulate human-like delay between selections (20-400ms)
            if (i < missing - 1) {
              const delay = Math.floor(Math.random() * 380) + 20;
              await new Promise(resolve => setTimeout(resolve, delay));
            }
          }
          
          console.log(`Selected fake players: ${chosenList.join(', ')}`);
          console.log(`Total selectedNumbers length after selection: ${game.selectedNumbers.length}`);
          io.emit('pickedNumbers', { roomId: game.roomId, numbers: game.selectedNumbers });
          
          // Immediately update and broadcast totals after fake player selection
          const realPlayers = game.players ? game.players.size : 0;
          const fakePlayersSelected = game.selectedNumbers.filter(n => n !== null).length;
          const totalSelectedCards = realPlayers + fakePlayersSelected;
          const broadcastWinAmount = totalSelectedCards * game.roomId * 0.78;
          
          io.emit("gameState", {
            gameId: game.id,
            roomId: game.roomId,
            pickedNumbers: game.selectedNumbers.filter(num => num !== null),
            total_players: totalSelectedCards,
            win_amount: broadcastWinAmount,
            game_status: game.status,
            count_down: game.countDown
          });
          
          // Add random pause between ticks (50-1200ms) to simulate human behavior
          const pauseDelay = Math.floor(Math.random() * 1150) + 50;
          await new Promise(resolve => setTimeout(resolve, pauseDelay));
        } else {
          console.log(`No more candidates available for fake selection`);
        }
      } else {
        console.log(`Fake selection complete: ${current}/${cap} players selected`);
      }
    } else {
      // Reset fake selection flags once game progresses
      if (game.fakeSelectionActive) {
      }
      game.fakeSelectionActive = false;
      game.fakeTargetCount = 0;
    }
    // Compute totals dynamically based on actual selected cards (real + fake)
    const realPlayers = game.players ? game.players.size : 0;
    const fakePlayersSelected = game.selectedNumbers.filter(n => n !== null).length;
    const totalSelectedCards = realPlayers + fakePlayersSelected;
    const broadcastTotalPlayers = totalSelectedCards;
    const broadcastWinAmount = broadcastTotalPlayers * game.roomId * 0.78;
    game.total_players = broadcastTotalPlayers;
    game.total_winAmount = broadcastWinAmount;

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers.filter(num => num !== null),
      total_players: broadcastTotalPlayers,
      win_amount: broadcastWinAmount,
      game_status: game.status,
      count_down: game.countDown
    });

  
  

  

    if (game.countDown === 0) {
      // Final check before starting game - ensure we have at least 1 player
      if (game.players.size < 1) {
        clearInterval(countdownInterval);
        game.isCountStart = false;
        game.countDown = game.countDown || 30;
        game.status = "waiting";
        
        io.emit("gameState", {
          gameId: game.id,
          roomId: game.roomId,
          pickedNumbers: game.selectedNumbers.filter(num => num !== null),
          total_players: game.total_players,
          
          game_status: game.status,
          count_down: game.countDown
        });
        
      
        
        return;
      }
      
      clearInterval(countdownInterval);
      game.isCountStart = false;
      game.status = "waiting";
      game.countDown = game.countDown || 30; // Reset countdown for next game
      game.currentCall = null;
      game.calledNumbers = [];
      game.selectedNumbers = game.selectedNumbers.filter(num => num !== null);

      // Freeze metrics at start (include actual selected cards)
      const realPlayersAtStart = game.players ? game.players.size : 0;
      const fakePlayersSelectedAtStart = game.selectedNumbers.filter(n => n !== null).length;
      const totalPlayersAtStart = realPlayersAtStart + fakePlayersSelectedAtStart;
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

  // Calculate total players (real + actual fake players selected)
  const realPlayers = game.players.size;
  const fakePlayersSelected = game.selectedNumbers.filter(n => n !== null).length;
  const totalPlayers = realPlayers + fakePlayersSelected;
  
  game.total_players = totalPlayers;
  game.fake_players = fakePlayersSelected;
  game.total_winAmount = totalPlayers * game.roomId * 0.78;

  try {
    await gameLossWallet(players, game.roomId, game.total_players, game.fake_players);
  
  } catch (error) {
    console.error('Error charging players:', error);
  }


 

  // Call first ball immediately when game starts
  const callBall = async () => {
    // Check if game has ended (winner announced)
    if (game.gameOver || game.status !== 'in-progress') {
      return;
    }
    
    const calledSet = new Set(game.calledNumbers.map(b => b.number));
    let ball = generateBalls();
    while (calledSet.has(ball.number)) {
      ball = generateBalls();
    }
    game.currentCall = ball;
    game.calledNumbers.push(ball);
    game.selectedNumbers = [];
    io.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
  
    // Schedule a fake winner based on dynamic settings (with live refresh)
    await refreshGameSettings(game);
    const callsThreshold = game.callsBeforeFakeWinner || 10;
    if (game.fakePlayersCanWin && !game.fakeWinnerScheduled && game.calledNumbers.length >= callsThreshold) {
      await scheduleFakeWinner(game);
    }

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      win_amount: game.win_amount,
      total_players: game.total_players,
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
  };

  // Call first ball immediately
  await callBall();

  // Then set up interval for subsequent balls
  const gameInterval = setInterval(callBall, game.gameSpeed);

  gameIntervals.set(game.id, [gameInterval]);
}

function generateFakeWinningCard() {
  // Generate a real bingo card with proper number ranges
  const grid = [];
  
  // B column: 1-15
  const bNumbers = generateRandomNumbers(1, 15, 5);
  // I column: 16-30
  const iNumbers = generateRandomNumbers(16, 30, 5);
  // N column: 31-45 (center is FREE)
  const nNumbers = generateRandomNumbers(31, 45, 4); // Only 4 numbers, center will be FREE
  // G column: 46-60
  const gNumbers = generateRandomNumbers(46, 60, 5);
  // O column: 61-75
  const oNumbers = generateRandomNumbers(61, 75, 5);
  
  // Create the grid structure
  for (let row = 0; row < 5; row++) {
    const rowCells = [];
    
    // B column
    rowCells.push({
      number: bNumbers[row],
      marked: false
    });
    
    // I column
    rowCells.push({
      number: iNumbers[row],
      marked: false
    });
    
    // N column
    if (row === 2) {
      // Center cell is FREE
      rowCells.push({
        number: '*',
        marked: false
      });
    } else {
      // Use N numbers for other rows
      const nIndex = row > 2 ? row - 1 : row; // Adjust index for center row
      rowCells.push({
        number: nNumbers[nIndex],
        marked: false
      });
    }
    
    // G column
    rowCells.push({
      number: gNumbers[row],
      marked: false
    });
    
    // O column
    rowCells.push({
      number: oNumbers[row],
      marked: false
    });
    
    grid.push(rowCells);
  }
  
  // Convert to column-major format (as expected by client)
  const columnGrid = [];
  for (let col = 0; col < 5; col++) {
    const column = [];
    for (let row = 0; row < 5; row++) {
      column.push(grid[row][col]);
    }
    columnGrid.push(column);
  }

  // Choose a random winning pattern
  const patterns = ['row', 'col', 'diag', 'anti', 'fourCorners', 'fourEdges'];
  const pick = patterns[Math.floor(Math.random() * patterns.length)];

  if (pick === 'row') {
    const r = Math.floor(Math.random() * 5);
    for (let c = 0; c < 5; c++) columnGrid[c][r].marked = true;
  } else if (pick === 'col') {
    const c = Math.floor(Math.random() * 5);
    for (let r = 0; r < 5; r++) columnGrid[c][r].marked = true;
  } else if (pick === 'diag') {
    for (let i = 0; i < 5; i++) columnGrid[i][i].marked = true;
  } else if (pick === 'anti') {
    for (let i = 0; i < 5; i++) columnGrid[4 - i][i].marked = true;
  } else if (pick === 'fourCorners') {
    columnGrid[0][0].marked = true;
    columnGrid[0][4].marked = true;
    columnGrid[4][0].marked = true;
    columnGrid[4][4].marked = true;
  } else if (pick === 'fourEdges') {
    // Cross-like edges as per client check
    columnGrid[2][0].marked = true;
    columnGrid[0][2].marked = true;
    columnGrid[2][4].marked = true;
    columnGrid[4][2].marked = true;
  }

  // Ensure center is always marked
  columnGrid[2][2].marked = true;

  return columnGrid;
}

// Helper function to generate random numbers within a range
function generateRandomNumbers(min, max, count) {
  const numbers = [];
  const used = new Set();
  
  while (numbers.length < count) {
    const num = Math.floor(Math.random() * (max - min + 1)) + min;
    if (!used.has(num)) {
      used.add(num);
      numbers.push(num);
    }
  }
  
  return numbers.sort((a, b) => a - b);
}

async function scheduleFakeWinner(game) {
  console.log("scheduleFakeWinner");
  try {
    // Check if fake players can win based on settings
    console.log("game.fakePlayersCanWin", game.fakePlayersCanWin);
    if (!game.fakePlayersCanWin) {
      return;
    }

    // Refresh settings periodically so dashboard toggles apply mid-game
    try {
      const now = Date.now();
      if (!game.lastSettingsFetchAt || (now - game.lastSettingsFetchAt) > 10000) { // 10s cache
        const latest = await getFakePlayerSettings();
        if (latest && typeof latest.fake_players_can_win === 'boolean') {
          game.fakePlayersCanWin = latest.fake_players_can_win;
        }
        if (latest && typeof latest.calls_before_fake_winner === 'number') {
          game.callsBeforeFakeWinner = latest.calls_before_fake_winner;
        }
        if (latest && typeof latest.max_fake_players === 'number') {
          game.maxFakePlayers = latest.max_fake_players;
        }
        game.lastSettingsFetchAt = now;
      }
    } catch (e) {}

    if (!game.fakePlayersCanWin) {
      return;
    }

    console.log("game.fakeWinnerScheduled", game.fakeWinnerScheduled);
    game.fakeWinnerScheduled = true;
    const delayMs = 5000 + Math.floor(Math.random() * 15000); // 5-20 seconds
    setTimeout(async () => {
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

        // Persist metrics at fake win moment and mark backend ended
        try {
          const realPlayers = g.players ? g.players.size : 0;
          // Use stored values instead of recalculating from selectedNumbers (which gets reset)
          const totalPlayers = g.total_players || 0;
          const fakePlayers = g.fake_players || 0;
          const winAmount = g.total_winAmount || 0;
          
          // (player, bet_amount, win_amount, total_players)
          await gameWinWallet("BOT_FAKE",g.roomId, winAmount, totalPlayers);
          
          // End the game after fake winner
          endGameDueToWinner(g);
        } catch (e) {
          // Error announcing fake winner
        }      
      } catch (err) {}
    }, delayMs);
  } catch (e) {
    // Error handling for scheduleFakeWinner
  }
}


function handleRefresh(data){
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
    console.log(`=== PLAYER JOINED DEBUG ===`);
    console.log(`Player joined with roomId: ${data.roomId}`);
    console.log(`Current active games keys: ${Array.from(activeGames.keys())}`);
    
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    let game = activeGames.get(roomIdStr);
    console.log(`Existing game found: ${!!game}`);
    
    if (!game) {
      console.log(`Creating new game for roomId: ${data.roomId}`);
      game = await createGame(roomIdStr);
      activeGames.set(roomIdStr, game);
      console.log(`New game created and stored with key: ${roomIdStr}`);
    } else {
      console.log(`Using existing game for roomId: ${data.roomId}`);
    }
    
    console.log(`Game status: ${game.status}`);
    console.log(`Game players: ${game.players?.size || 0}`);
    console.log(`=== END PLAYER JOINED DEBUG ===`);
    
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
    console.log(`=== JOIN GAME DEBUG ===`);
    console.log(`Join game request:`, data);
    console.log(`Looking for game with roomId: ${data.roomId}`);
    console.log(`Current active games keys: ${Array.from(activeGames.keys())}`);
    
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    const game = activeGames.get(roomIdStr);
    console.log(`Game found: ${!!game}`);
    console.log(`Game status: ${game?.status}`);
    console.log(`Game players: ${game?.players?.size || 0}`);
    
    if (!data.playerId || !game) {
      console.log(`❌ Missing playerId or game not found`);
      console.log(`playerId: ${data.playerId}, game: ${!!game}`);
      return;
    }

    if (game.status === 'in-progress') {
      console.log(`❌ Game already in progress`);
      socket.emit('joinError', {
        roomId: data.roomId,
        message: 'Game is already in progress. Please wait for the next round.'
      });
      return;
    }
    
    console.log(`✅ Game found and ready for joining`);

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

    const realPlayers = game.players ? game.players.size : 0;
    const fakePlayersSelected = game.selectedNumbers.filter(n => n !== null).length;
    const total_players = realPlayers + fakePlayersSelected;

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
    console.log('=== BINGO EVENT DEBUG ===');
    console.log('Bingo event received:', data);
    console.log('Active games keys:', Array.from(activeGames.keys()));
    console.log('Active games count:', activeGames.size);
    
    // Debug: Log all active games
    console.log('=== ALL ACTIVE GAMES ===');
    for (const [key, game] of activeGames.entries()) {
      console.log(`Game key: ${key}, Status: ${game.status}, Players: ${game.players?.size || 0}`);
    }
    console.log('=== END ACTIVE GAMES ===');
    
    // If player previously made a false bingo, ignore further bingo attempts
    console.log(`Looking for disqualification check with roomId: ${data.roomId}`);
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    const gameForFaulCheck = activeGames.get(roomIdStr);
    console.log('Game for fault check found:', !!gameForFaulCheck);
    
    if (gameForFaulCheck && gameForFaulCheck.fauldMadePlayers && gameForFaulCheck.fauldMadePlayers.get && gameForFaulCheck.fauldMadePlayers.get(data.playerId) === true) {
      console.log('Player is disqualified for false bingo:', data.playerId);
      socket.emit("disqualified", { message: "You are disqualified for this round due to false bingo.", roomId: data.roomId, gameId: data.gameId });
      return;
    }

    console.log(`Looking for game with roomId: ${data.roomId} (converted to string: ${roomIdStr})`);
    const game = activeGames.get(roomIdStr);
    console.log('Game found:', !!game);
    console.log('Game status:', game?.status);
    console.log('Game players:', game?.players?.size || 0);
    
    if (!game || game.status !== 'in-progress') {
      console.log('❌ Game not found or not in progress:', { 
        roomId: data.roomId, 
        roomIdStr: roomIdStr,
        gameStatus: game?.status,
        gameExists: !!game,
        activeGamesKeys: Array.from(activeGames.keys())
      });
      return;
    }
    
    console.log('✅ Game found and in progress!');
    
    const playerCards = game.players.get(data.playerId);
    if (!playerCards || !Array.isArray(playerCards)) {
      console.log('Player cards not found:', { playerId: data.playerId, playerCards });
      return;
    }
    
    console.log('Processing bingo for player:', data.playerId);
    const board = data.board
    const boardNumber = data.boardNumber
    console.log('Board data:', { board, boardNumber, calledNumbers: game.calledNumbers });
    
    const markedSingleCard = markPlayerCard(board, game.calledNumbers)
    console.log('Marked card:', markedSingleCard);
    
    const isSingleBingo = checkSingleCardBingo(markedSingleCard)
    console.log('Is single bingo:', isSingleBingo);
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
      });

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

      endGameDueToWinner(game);
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
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    const game = activeGames.get(roomIdStr);
    if (!game) {
      return;
    }
    

    const playerId = data.playerId
    const selectedNumber = data.selectedNumber
    const selectedNumber2 = data.selectedNumber2 || null // Handle case where selectedNumber2 might not be provided
    
    // If game is in progress, preserve player data for potential reconnection
    if (game.status === 'in-progress') {
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
      }
   
      
      // Immediate verification
      const storedData = game.disconnectedPlayers.get(playerId);
      if (storedData) {
      } else {
      }
      
      // Remove from active players but keep in selectedNumbers for game continuity
      if (game?.players?.has(playerId)) {
        game.players.delete(playerId);
      }
      
      // Don't remove from selectedNumbers for in-progress games
      // This allows the game to continue with the same player count
      
    } else {
      // For waiting games, remove completely as before
      if (game?.players?.has(playerId)) {
        game.players.delete(playerId);
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
      total_players: game.total_players,
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
      clearGameIntervals(game.id);
      game.isCountStart = false;
      game.countDown = game.countDown || 30;
      game.status = "waiting";
      
      // Emit updated game state
      io.emit("gameState", {
        gameId: game.id,
        roomId: game.roomId,
        pickedNumbers: game.selectedNumbers,
        total_players: game.total_players,
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
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    const game = activeGames.get(roomIdStr);
    if (!game) {
      return;
    }

    const playerSelections = [];
    for (const [playerId, numbers] of game.selectedNumbersToPlayer.entries()) {
      playerSelections.push({
        playerId,
        selectedNumbers: numbers
      });
    }
    
  
    
    socket.emit("allPlayerSelections", {
      players: playerSelections,
      game_status: game.status
    });
  });

  // Handle game rejoin
  socket.on("rejoinGame", (data) => {
    const roomIdStr = String(data.roomId); // Convert to string for consistent lookup
    const game = activeGames.get(roomIdStr);
    
    if (!game) {
      socket.emit("rejoinError", { message: "Game not found" });
      return;
    }

    // Check if player has disconnected data
    if (!game.disconnectedPlayers || !game.disconnectedPlayers.has(data.playerId)) {
      socket.emit("rejoinError", { message: "No previous game data found" });
      return;
    }

    const playerData = game.disconnectedPlayers.get(data.playerId);

    
    // If player had made a false bingo (faul), disqualify and do not restore to active game
    const wasFaulMade = !!(game.fauldMadePlayers && game.fauldMadePlayers.get && game.fauldMadePlayers.get(data.playerId) === true);
    if (wasFaulMade) {

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

  });

  socket.on("disconnect", () => {
   
    const user = users.get(socket.id);
    if (user) {
      const roomIdStr = String(user.gameId);
      const game = activeGames.get(roomIdStr);
      const playerId = user.playerId
   
      if (!game) {
        users.delete(socket.id);
        return;
      }

      if (game.selectedNumbersToPlayer && game.selectedNumbersToPlayer.has(playerId)){
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
            total_players: game.total_players,
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
            clearGameIntervals(game.id);
            game.isCountStart = false;
            game.countDown = game.countDown || 30;
            game.status = "waiting";
            
            // Emit updated game state
            io.emit("gameState", {
              gameId: game.id,
              roomId: game.roomId,
              pickedNumbers: game.selectedNumbers,
              total_players: game.total_players,
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

  // Handle promotion events
  socket.on('promotion_viewed', (data) => {
    console.log('Promotion viewed:', data);
    // Track promotion view in database
    // This could be sent to Django backend via HTTP request
  });

  socket.on('promotion_clicked', (data) => {
    console.log('Promotion clicked:', data);
    // Track promotion click in database
    // This could be sent to Django backend via HTTP request
  });

  socket.on('promotion_closed', (data) => {
    console.log('Promotion closed:', data);
    // Track promotion dismissal
  });

});

app.use(express.static(path.join(__dirname, './build')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, './build', 'index.html'));
});

const PORT = process.env.PORT || 5000
const IP = ip.address();
server.listen(PORT, () => {
  // Server running on port ${PORT} and IP ${IP}
  console.log(`Server running on port ${PORT} and IP ${IP}`);
});



