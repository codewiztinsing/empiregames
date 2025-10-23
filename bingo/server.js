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
const fetch = require('node-fetch');
dotenv.config();

// Global variable to store current settings
let currentGameSettings = null;
const app = express();
app.use(cors());
const server = http.createServer(app);


const fetchGameSettings = async () => {
  try {
    const BASE_URL = process.env.DASHBOARD_BASE_URL || 'https://akerbingo.com';
    const res = await fetch(`${BASE_URL}/game/api/fake-player-settings/public/`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    let fake = { fake_players_count: 0, fake_can_win: false, fake_win_after_calls: 10 };
    if (res.ok) {
      const j = await res.json();
      if (j && j.data) fake = j.data;
    }
    // also get main game settings via existing helper if available
    const gameSpeed = Number(process.env.GAME_SPEED || 4000);
    const countDown = Number(process.env.COUNT_DOWN || 30);
    const newSettings = {
      gameSpeed,
      countDown,
      fakePlayersCount: Number(fake.fake_players_count || 0),
      fakeCanWin: !!fake.fake_can_win,
      fakeWinAfterCalls: Number(fake.fake_win_after_calls || 10),
    };
    console.log("🔄 Fetched latest game settings:", newSettings);
    return newSettings;
  } catch (e) {
    console.error("Error fetching game settings:", e);
  return {
      gameSpeed: Number(process.env.GAME_SPEED || 4000),
      countDown: Number(process.env.COUNT_DOWN || 30),
      fakePlayersCount: Number(process.env.FAKE_PLAYERS_COUNT || 0),
      fakeCanWin: String(process.env.FAKE_CAN_WIN || 'false') === 'true',
      fakeWinAfterCalls: Number(process.env.FAKE_WIN_AFTER_CALLS || 10),
    };
  }
};

const getConstant = async () => {
  // Return cached settings if available, otherwise fetch fresh
  if (currentGameSettings) {
    return currentGameSettings;
  }
  currentGameSettings = await fetchGameSettings();
  return currentGameSettings;
};

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
    gameSpeed: gameSettings.gameSpeed,
    // Dynamic fake configuration loaded from dashboard API
    fakeSettings: {
      fakePlayersCount: Number(gameSettings.fakePlayersCount || 0),
      fakeCanWin: !!gameSettings.fakeCanWin,
      fakeWinAfterCalls: Number(gameSettings.fakeWinAfterCalls || 10)
    },
    // Static total players calculated once at game creation
    staticTotalPlayers: null,
    staticWinAmount: null,
    disconnectedPlayers: new Map(),
    fauldMadePlayers: new Map(),
    // Fake picks during countdown (do not create real players)
    fakePickedNumbers: new Set(),
    roomId
  };
  activeGames.set(roomId, game);
  
  // If fake players are configured, start countdown immediately
  if (game.fakeSettings.fakePlayersCount > 0) {
    console.log("🤖 Fake players configured - starting countdown immediately for game:", game.id);
    setTimeout(() => {
      startCountDown(game);
    }, 1000); // Small delay to ensure game is properly initialized
  }
  
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
  // Reset fake picked numbers for immediate selection
  game.fakePickedNumbers = new Set();

  for (const [socketId, user] of users.entries()) {
    if (user.gameId === game.id) users.delete(socketId);
  }

  const data = await updateLastGame(game.roomId);
  
  // Start fake player number selection immediately if configured
  if (game.fakeSettings?.fakePlayersCount > 0) {
    console.log("🤖 Game ended - starting fake player number selection immediately");
    // Start countdown immediately for fake players
    setTimeout(() => {
      startCountDown(game);
    }, 500); // Small delay to ensure game state is properly reset
  } else {
    startCountDown(game);
  }

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
  
  // Calculate static total players once at countdown start
  if (!game.staticTotalPlayers) {
    const realPlayers = game.players.size;
    const fakePlayers = game.fakeSettings?.fakePlayersCount > 0 ? game.fakeSettings.fakePlayersCount : 0;
    let total = realPlayers + fakePlayers;
    
    if (total < 10) {
      game.staticTotalPlayers = 10; // minimum 10 players
    } else {
      // Pick a random number between 10 and total (inclusive) - but only once
      game.staticTotalPlayers = Math.floor(Math.random() * (total - 10 + 1)) + 10;
    }
    
    game.staticWinAmount = game.staticTotalPlayers * game.roomId * 0.78;
    console.log("🎯 Static total players calculated - real:", realPlayers, "fake:", fakePlayers, "static total:", game.staticTotalPlayers, "static win:", game.staticWinAmount);
  }
  
  // Allow countdown to start if we have fake players configured, even with 0 real players
  const hasFakePlayers = game.fakeSettings?.fakePlayersCount > 0;
  const hasEnoughPlayers = game.players && game.players.size >= 2;
  const canStartWithFakeOnly = hasFakePlayers && game.players && game.players.size >= 0;
  
  if (game.isCountStart || !game.players || (!hasEnoughPlayers && !canStartWithFakeOnly)) {
    console.log("❌ Cannot start countdown - isCountStart:", game.isCountStart, "players:", game.players?.size, "hasFakePlayers:", hasFakePlayers);
    return;
  }
  clearGameIntervals(game.id);
  game.countDown = 30; // Always reset to 30 when starting countdown
  game.isCountStart = true;
  console.log("⏰ Countdown started for game:", game.id, "countdown:", game.countDown);

  // Initialize a lightweight tick counter to pace fake picks
  if (typeof game._fakePickTick !== 'number') {
    game._fakePickTick = 0;
  }

  const countdownInterval = setInterval(() => {
    console.log("⏱️ Countdown tick - game:", game.id, "countdown:", game.countDown, "players:", game.players.size);
    game._fakePickTick = (game._fakePickTick + 1) % 1000000; // prevent overflow
    
    // Check if we still have enough players during countdown (allow fake players to continue)
    const hasFakePlayersDuringCountdown = game.fakeSettings?.fakePlayersCount > 0;
    const hasEnoughPlayersDuringCountdown = game.players.size >= 2;
    const canContinueWithFakeOnly = hasFakePlayersDuringCountdown && game.players.size >= 0;
    
    if (!hasEnoughPlayersDuringCountdown && !canContinueWithFakeOnly) {
      console.log("🔄 Not enough players during countdown - resetting countdown");
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
    // Fill fake picks toward configured fakePlayersCount and cap there
    try {
      const targetFakePlayers = (game.fakeSettings && typeof game.fakeSettings.fakePlayersCount === 'number')
        ? Math.max(0, game.fakeSettings.fakePlayersCount)
        : 0;

      if (!game.fakePickedNumbers) game.fakePickedNumbers = new Set();

      // If target is zero, keep fake picks empty during countdown
      if (targetFakePlayers === 0) {
        game.fakePickedNumbers.clear();
      } else {
        // Ensure we do not exceed the configured target
        if (game.fakePickedNumbers.size > targetFakePlayers) {
          // Trim excess picks deterministically by deleting extras
          const toRemove = game.fakePickedNumbers.size - targetFakePlayers;
          let removed = 0;
          for (const val of game.fakePickedNumbers) {
            game.fakePickedNumbers.delete(val);
            removed++;
            if (removed >= toRemove) break;
          }
        }

        // Gradually fill up to the target, paced to feel very human-like
        const remaining = targetFakePlayers - game.fakePickedNumbers.size;
        let toAdd = 0;

        // Much slower pace: add only every 3-4 seconds to mimic real players
        const shouldAttemptThisTick = (game._fakePickTick % 3 === 0);

        if (shouldAttemptThisTick && remaining > 0) {
          // Very slow base rate: approach target very gradually
          const secondsLeft = Math.max(1, game.countDown);
          const baseRate = Math.ceil(remaining / (secondsLeft * 2)); // Much slower approach

          // Very small bursts (1-2 max) to feel like individual players joining
          toAdd = Math.min(1, Math.max(0, baseRate));

          // More random jitter: often skip cycles to feel organic
          if (Math.random() < 0.5 && toAdd > 0) {
            toAdd = 0; // Skip this cycle entirely
          }

          // In final 5 seconds, slightly increase but still gradual
          if (game.countDown <= 5) {
            toAdd = Math.min(2, remaining, Math.max(toAdd, 0));
            // Still random chance to skip even in final seconds
            if (Math.random() < 0.3) {
              toAdd = 0;
            }
          }
        }

        if (toAdd > 0) {
          const used = new Set([...realPicks, ...game.fakePickedNumbers]);
          for (let k = 0; k < toAdd; k++) {
            let pick = Math.floor(Math.random() * 400) + 1;
            let attempts = 0;
            while (used.has(pick) && attempts < 800) {
              pick = Math.floor(Math.random() * 400) + 1;
              attempts++;
            }
            used.add(pick);
            game.fakePickedNumbers.add(pick);
          }
        }
      }

      fakePicksSnapshot = Array.from(game.fakePickedNumbers);
    } catch (e) {}

    const displayTotal = (realPicks?.length || 0) + (fakePicksSnapshot?.length || 0);
    const displayWin = displayTotal * game.roomId * 0.78;

    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: { numbers: realPicks, fake: fakePicksSnapshot },
      total_players: displayTotal,
      win_amount: displayWin,
      game_status: game.status,
      count_down: game.countDown
    });

    io.emit("globals", {
      roomId: game.roomId,
      countDown: game.countDown
    })
  

  

    if (game.countDown === 0) {
      // Final check before starting game - allow fake players to start game
      const hasFakePlayersAtStart = game.fakeSettings?.fakePlayersCount > 0;
      const hasEnoughPlayersAtStart = game.players.size >= 2;
      const canStartWithFakeOnlyAtStart = hasFakePlayersAtStart && game.players.size >= 0;
      
      if (!hasEnoughPlayersAtStart && !canStartWithFakeOnlyAtStart) {
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
      // Calculate total players based on actual picked numbers (real + fake)
      const realPlayersCount = game.selectedNumbers.filter(num => num !== null).length;
      const fakePlayersCount = game.fakePickedNumbers ? game.fakePickedNumbers.size : 0;
      game.total_players = realPlayersCount + fakePlayersCount;
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

 

  const emitNextBall = async () => {
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

    console.log("game.fakeSettings?.fakePlayersCount",game.fakeSettings?.fakePlayersCount)
    console.log("game.total_players (real players):", game.total_players)
    console.log("game.staticTotalPlayers:", game.staticTotalPlayers)
    console.log("game.staticWinAmount:", game.staticWinAmount)
    console.log("game.roomId:", game.roomId)
    console.log("game.win_amount (base):", game.win_amount)

    // Calculate total players based on actual picked numbers (real + fake)
    const realPlayersCount = game.selectedNumbers.filter(num => num !== null).length;
    const fakePlayersCount = game.fakePickedNumbers ? game.fakePickedNumbers.size : 0;
    const actualTotalPlayers = realPlayersCount + fakePlayersCount;
  
    io.emit("gameState", {
      gameId: game.id,
      roomId: game.roomId,
      pickedNumbers: game.selectedNumbers,
      game_status: game.status,
      count_down: game.countDown,
      // Use actual picked numbers count to match pickedNumbers
      total_players: actualTotalPlayers,
      win_amount: actualTotalPlayers * game.roomId * 0.78,
      lastBall: ball,
      called_numbers: game.calledNumbers,
      total_called_numbers: game.calledNumbers.length,

    });

    // After configured calls, if allowed and no real winner yet, emit a fake winner that mimics real flow
    try {
      if (game.fakeSettings?.fakeCanWin && !game.winner && game.calledNumbers.length === (game.fakeSettings.fakeWinAfterCalls || 10)) {
        const ETH_MEN = [
          'Abebe','Kebede','Haile','Tesfaye','Getachew',
          'Bekele','Alemu','Yohannes','Tadesse','Mekonnen',
          'Solomon','Fikadu','Demeke','Mulugeta','Abate',
          'Zewdu','Tewodros','Eshetu','Desta','Ayalew'
        ];
        // Use fixed fake player ID for transaction purposes
        const fakeId = 9999999999; // Fixed fake player ID
        const fakeName = ETH_MEN[Math.floor(Math.random() * ETH_MEN.length)];

        // Generate a proper 5x5 bingo board using only 5 called numbers for winning pattern
        const generateFakeWinningBoard = () => {
          const board = Array.from({ length: 5 }, () => Array.from({ length: 5 }, () => ({ number: 0, marked: false })));
          
          // Get called numbers for realistic board
          const calledNumbers = game.calledNumbers.map(ball => ball.number);
          console.log('🎯 Using called numbers for fake board:', calledNumbers);
          
          // Fill board with valid bingo numbers (B:1-15, I:16-30, N:31-45, G:46-60, O:61-75)
          const columnRanges = [
            { start: 1, end: 15 },   // B
            { start: 16, end: 30 },   // I
            { start: 31, end: 45 },   // N
            { start: 46, end: 60 },   // G
            { start: 61, end: 75 }    // O
          ];
          
          // First, fill the entire board with random numbers (not called numbers)
          const usedNumbers = new Set();
          for (let col = 0; col < 5; col++) {
            const range = columnRanges[col];
            
            for (let row = 0; row < 5; row++) {
              if (col === 2 && row === 2) {
                // Free space in center
                board[row][col] = { number: '*', marked: true };
              } else {
                let num;
                do {
                  num = Math.floor(Math.random() * (range.end - range.start + 1)) + range.start;
                } while (usedNumbers.has(num));
                
                usedNumbers.add(num);
                board[row][col] = { number: num, marked: false };
              }
            }
          }
          
          // Randomly choose ONE winning condition
          const winningConditions = [
            'row',      // Horizontal line
            'column',   // Vertical line  
            'diagonal1', // Top-left to bottom-right
            'diagonal2', // Top-right to bottom-left
            'corners'   // Four corners
          ];
          
          const chosenCondition = winningConditions[Math.floor(Math.random() * winningConditions.length)];
          console.log(`🎯 Fake winner using ${chosenCondition} pattern`);
          
          // Use only 5 called numbers to fulfill the chosen winning condition
          const calledNumbersToUse = calledNumbers.slice(0, 5);
          console.log(`🎯 Using these 5 called numbers for winning pattern:`, calledNumbersToUse);
          
          // Apply the winning pattern using called numbers
          switch (chosenCondition) {
            case 'row':
              // Random horizontal line using called numbers
              const winningRow = Math.floor(Math.random() * 5);
              for (let col = 0; col < 5; col++) {
                if (col < calledNumbersToUse.length) {
                  board[winningRow][col].number = calledNumbersToUse[col];
                  board[winningRow][col].marked = true;
                }
              }
              console.log(`🎯 Row ${winningRow} marked as winning with called numbers`);
              break;
              
            case 'column':
              // Random vertical line using called numbers
              const winningCol = Math.floor(Math.random() * 5);
              for (let row = 0; row < 5; row++) {
                if (row < calledNumbersToUse.length) {
                  board[row][winningCol].number = calledNumbersToUse[row];
                  board[row][winningCol].marked = true;
                }
              }
              console.log(`🎯 Column ${winningCol} marked as winning with called numbers`);
              break;
              
            case 'diagonal1':
              // Diagonal top-left to bottom-right using called numbers
              for (let i = 0; i < 5; i++) {
                if (i < calledNumbersToUse.length) {
                  board[i][i].number = calledNumbersToUse[i];
                  board[i][i].marked = true;
                }
              }
              console.log(`🎯 Diagonal1 (top-left to bottom-right) marked as winning with called numbers`);
              break;
              
            case 'diagonal2':
              // Diagonal top-right to bottom-left using called numbers
              for (let i = 0; i < 5; i++) {
                if (i < calledNumbersToUse.length) {
                  board[i][4-i].number = calledNumbersToUse[i];
                  board[i][4-i].marked = true;
                }
              }
              console.log(`🎯 Diagonal2 (top-right to bottom-left) marked as winning with called numbers`);
              break;
              
            case 'corners':
              // Four corners using called numbers
              const cornerPositions = [[0,0], [0,4], [4,0], [4,4]];
              for (let i = 0; i < Math.min(4, calledNumbersToUse.length); i++) {
                const [row, col] = cornerPositions[i];
                board[row][col].number = calledNumbersToUse[i];
                board[row][col].marked = true;
              }
              console.log(`🎯 Four corners marked as winning with called numbers`);
              break;
          }
          
          // Debug: Log the complete board structure
          console.log('🎯 Complete fake winning board:');
          board.forEach((row, rowIndex) => {
            const rowStr = row.map(cell => `${cell.number}${cell.marked ? '✓' : ' '}`).join(' | ');
            console.log(`Row ${rowIndex}: ${rowStr}`);
          });
          
          // Count total numbers and marked cells
          let totalNumbers = 0;
          let markedCells = 0;
          board.forEach(row => {
            row.forEach(cell => {
              if (cell.number !== '*') totalNumbers++;
              if (cell.marked) markedCells++;
            });
          });
          console.log(`🎯 Board summary: ${totalNumbers} numbers generated, ${markedCells} cells marked for winning pattern`);
          
          return board;
        };

        const winningCard = generateFakeWinningBoard();

        // Transpose the board from [row][col] to [col][row] format for client compatibility
        const transposedCard = Array.from({ length: 5 }, (_, colIndex) => 
          Array.from({ length: 5 }, (_, rowIndex) => winningCard[rowIndex][colIndex])
        );

        console.log('🎯 Transposed card for client:', JSON.stringify(transposedCard, null, 2));

        game.winner = fakeId;

        // Call win API for fake player
        try {
          const fakeWinAmount = game.total_winAmount || (game.staticWinAmount || 1000);
          const fakeTotalPlayers = game.staticTotalPlayers || game.total_players || 10;
          
          console.log('🎯 Calling win API for fake player:', {
            player: fakeId,
            bet_amount: game.roomId,
            win_amount: fakeWinAmount,
            total_players: fakeTotalPlayers,
            game_id: game.id
          });
          
          await gameWinWallet(fakeId, game.roomId, fakeWinAmount, fakeTotalPlayers);
          console.log('✅ Fake player win API called successfully');
        } catch (error) {
          console.error('❌ Error calling win API for fake player:', error);
        }

        io.emit("winBingo", {
          isBingo: true,
          playerId: fakeId,
          markedCells: transposedCard,
          winningCard: transposedCard,
          winner: fakeId,
          calledNumbers: game.calledNumbers,
          playerCard: 1,
          winner_Number: 1,
          playerName: fakeName,
          currentCall: game.currentCall,
          gameId: game.id,
          total_winAmount: game.total_winAmount,
          total_players: game.total_players + (game.fakePickedNumbers ? game.fakePickedNumbers.size : 0),
          roomId: game.roomId
        });

        io.emit("bingoWinner", {
          isBingo: true,
          playerId: fakeId,
          markedCells: transposedCard,
          winningCard: transposedCard,
          winner: fakeId,
          winnerCardNumber: 1,
          winnerPlayerName: fakeName,
          gameId: game.id,
          roomId: game.roomId
        });

        // End the game immediately after fake player wins
        console.log('🎯 Ending game immediately after fake player win');
        // Clear all intervals to stop the game immediately
        clearGameIntervals(game.id);
        game.status = "finished";
        game.winner = fakeId;
        
        // Emit game over immediately
        io.emit("gameOver", {
          gameId: game.id,
          roomId: game.roomId,
          winner: fakeId,
          winnerName: fakeName,
          total_winAmount: game.total_winAmount,
          total_players: game.total_players + (game.fakePickedNumbers ? game.fakePickedNumbers.size : 0)
        });
        
        // Reset game state for next game
        setTimeout(() => {
          // Reset game state similar to endGame but keep players
          clearGameIntervals(game.id);
          game.calledNumbers = [];
          game.currentCall = null;
          game.status = "waiting";
          game.gameOver = false;
          game.winner = null;
          game.countDown = 30;
          game.isCountStart = false;
          game.fauldMadePlayers.clear();
          game.staticTotalPlayers = null;
          game.staticWinAmount = null;
          game.fakePickedNumbers = new Set();
          
          // Start fake player number selection immediately for next game
          console.log("🤖 Fake player won - starting fake player number selection immediately for next game");
          setTimeout(() => {
            startCountDown(game);
          }, 500); // Small delay to ensure game state is properly reset
          
      io.emit("gameStatus", {
            status: "waiting",
        roomId: game.roomId,
            gameId: game.id
          });
        }, 1000);
        return; // stop further emission for this tick
      }
    } catch (e) {}

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
  const gameInterval = setInterval(async () => {
    await emitNextBall();
  }, game.gameSpeed);

  gameIntervals.set(game.id, [gameInterval]);
}


function handleRefresh(data){
  console.log("handleRefresh", data)
  const game = activeGames.get(data.gameId);
  if (!game) return;
  
  // Calculate total players based on actual picked numbers (real + fake)
  const realPlayersCount = game.selectedNumbers.filter(num => num !== null).length;
  const fakePlayersCount = game.fakePickedNumbers ? game.fakePickedNumbers.size : 0;
  const actualTotalPlayers = realPlayersCount + fakePlayersCount;
  
  io.emit("gameState", {
    gameId: game.id,
    roomId: game.roomId,
    // Use actual picked numbers count to match pickedNumbers
    total_players: actualTotalPlayers,
    pickedNumbers: game.selectedNumbers,
    game_status: game.status,
    count_down: game.countDown,
    win_amount: actualTotalPlayers * game.roomId * 0.78,
    lastBall: game.currentCall,
    called_numbers: game.calledNumbers,
    total_called_numbers: game.calledNumbers.length,
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

// Initialize settings on startup
fetchGameSettings().then(settings => {
  currentGameSettings = settings;
  console.log("🚀 Initial game settings loaded:", settings);
});

// Periodic fetch every 10 seconds to reflect latest changes
setInterval(async () => {
  try {
    const newSettings = await fetchGameSettings();
    const hasChanged = !currentGameSettings || 
      currentGameSettings.fakePlayersCount !== newSettings.fakePlayersCount ||
      currentGameSettings.fakeCanWin !== newSettings.fakeCanWin ||
      currentGameSettings.fakeWinAfterCalls !== newSettings.fakeWinAfterCalls ||
      currentGameSettings.gameSpeed !== newSettings.gameSpeed ||
      currentGameSettings.countDown !== newSettings.countDown;
    
    if (hasChanged) {
      console.log("🔄 Game settings updated:", newSettings);
      currentGameSettings = newSettings;
      
      // Update existing games with new settings
      activeGames.forEach((game, gameId) => {
        if (game.fakeSettings) {
          game.fakeSettings = {
            fakePlayersCount: newSettings.fakePlayersCount,
            fakeCanWin: newSettings.fakeCanWin,
            fakeWinAfterCalls: newSettings.fakeWinAfterCalls,
          };
          console.log(`🔄 Updated fake settings for game ${gameId}:`, game.fakeSettings);
        }
      });
    }
  } catch (error) {
    console.error("❌ Error during periodic settings fetch:", error);
  }
}, 10000); // 10 seconds

server.listen(PORT, () => console.log(`Server running on port ${PORT} and IP ${IP}`));



