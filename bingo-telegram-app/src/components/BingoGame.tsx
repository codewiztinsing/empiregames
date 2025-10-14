import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { WebApp } from '../utils/telegram';

interface User {
  id: number;
  username: string;
  phone: string;
  telegram_id: string;
  balance: number;
}

interface BingoGameProps {
  user: User | null;
}

interface BingoCard {
  id: number;
  numbers: number[][];
  marked: boolean[][];
}

const BingoGame: React.FC<BingoGameProps> = ({ user }) => {
  const navigate = useNavigate();
  const [gameStarted, setGameStarted] = useState(false);
  const [bingoCard, setBingoCard] = useState<BingoCard | null>(null);
  const [calledNumbers, setCalledNumbers] = useState<number[]>([]);
  const [currentNumber, setCurrentNumber] = useState<number | null>(null);
  const [gameTime, setGameTime] = useState(0);
  const [isBingo, setIsBingo] = useState(false);
  const [betAmount, setBetAmount] = useState(10);

  // Generate a random bingo card
  const generateBingoCard = (): BingoCard => {
    const numbers: number[][] = [];
    const marked: boolean[][] = [];

    for (let i = 0; i < 5; i++) {
      numbers[i] = [];
      marked[i] = [];
      for (let j = 0; j < 5; j++) {
        if (i === 2 && j === 2) {
          // Free space in the center
          numbers[i][j] = 0;
          marked[i][j] = true;
        } else {
          // Generate random number for this column
          const min = j * 15 + 1;
          const max = (j + 1) * 15;
          numbers[i][j] = Math.floor(Math.random() * (max - min + 1)) + min;
          marked[i][j] = false;
        }
      }
    }

    return { id: Date.now(), numbers, marked };
  };

  // Check for bingo
  const checkBingo = (card: BingoCard): boolean => {
    // Check rows
    for (let i = 0; i < 5; i++) {
      if (card.marked[i].every(marked => marked)) {
        return true;
      }
    }

    // Check columns
    for (let j = 0; j < 5; j++) {
      if (card.marked.every(row => row[j])) {
        return true;
      }
    }

    // Check diagonals
    if (card.marked.every((row, i) => row[i])) {
      return true;
    }
    if (card.marked.every((row, i) => row[4 - i])) {
      return true;
    }

    return false;
  };

  // Mark number on card
  const markNumber = (number: number) => {
    if (!bingoCard) return;

    const newCard = { ...bingoCard };
    let found = false;

    for (let i = 0; i < 5; i++) {
      for (let j = 0; j < 5; j++) {
        if (newCard.numbers[i][j] === number) {
          newCard.marked[i][j] = true;
          found = true;
        }
      }
    }

    if (found) {
      setBingoCard(newCard);
      if (checkBingo(newCard)) {
        setIsBingo(true);
        WebApp.showAlert('🎉 BINGO! You won!');
      }
    }
  };

  // Start game
  const startGame = () => {
    if (!user || user.balance < betAmount) {
      WebApp.showAlert('Insufficient balance!');
      return;
    }

    setGameStarted(true);
    setBingoCard(generateBingoCard());
    setCalledNumbers([]);
    setCurrentNumber(null);
    setGameTime(0);
    setIsBingo(false);

    // Simulate number calling
    const interval = setInterval(() => {
      if (isBingo) {
        clearInterval(interval);
        return;
      }

      let newNumber: number;
      do {
        newNumber = Math.floor(Math.random() * 75) + 1;
      } while (calledNumbers.includes(newNumber));

      setCalledNumbers(prev => [...prev, newNumber]);
      setCurrentNumber(newNumber);
      markNumber(newNumber);

      if (calledNumbers.length >= 74) {
        clearInterval(interval);
      }
    }, 3000);

    // Game timer
    const timerInterval = setInterval(() => {
      setGameTime(prev => prev + 1);
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timerInterval);
    };
  };

  // Format time
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!gameStarted) {
    return (
      <div className="min-h-screen p-4">
        <div className="text-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg mb-4"
          >
            ← Back to Home
          </button>
          <div className="text-6xl mb-4">🎯</div>
          <h1 className="text-3xl font-bold text-white mb-2">Bingo Game</h1>
          <p className="text-gray-300">Choose your bet amount and start playing!</p>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/20">
          <h3 className="text-lg font-semibold text-white mb-4">Bet Amount</h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[10, 25, 50, 100, 200, 500].map((amount) => (
              <button
                key={amount}
                onClick={() => setBetAmount(amount)}
                className={`p-3 rounded-lg font-semibold transition-colors ${
                  betAmount === amount
                    ? 'bg-purple-600 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                {amount} ETB
              </button>
            ))}
          </div>
          <div className="text-center">
            <p className="text-gray-300 text-sm mb-4">
              Your Balance: {user?.balance || 0} ETB
            </p>
            <button
              onClick={startGame}
              disabled={!user || user.balance < betAmount}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 text-white px-8 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 disabled:transform-none"
            >
              Start Game ({betAmount} ETB)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => navigate('/')}
          className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg"
        >
          ← Home
        </button>
        <div className="text-center">
          <div className="text-white font-semibold">Game Time: {formatTime(gameTime)}</div>
          <div className="text-sm text-gray-300">Bet: {betAmount} ETB</div>
        </div>
      </div>

      {/* Current Number */}
      {currentNumber && (
        <div className="text-center mb-6">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 inline-block">
            <div className="text-sm text-white/80 mb-2">Current Number</div>
            <div className="text-4xl font-bold text-white">{currentNumber}</div>
          </div>
        </div>
      )}

      {/* Bingo Card */}
      {bingoCard && (
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 mb-6 border border-white/20">
          <div className="grid grid-cols-5 gap-2">
            {bingoCard.numbers.map((row, i) =>
              row.map((number, j) => (
                <div
                  key={`${i}-${j}`}
                  className={`aspect-square flex items-center justify-center rounded-lg font-bold text-sm transition-all ${
                    bingoCard.marked[i][j]
                      ? 'bg-green-500 text-white'
                      : 'bg-white/20 text-gray-300'
                  } ${number === 0 ? 'bg-purple-500 text-white' : ''}`}
                >
                  {number === 0 ? 'FREE' : number}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Called Numbers */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-4 mb-6 border border-white/20">
        <h3 className="text-lg font-semibold text-white mb-3">Called Numbers</h3>
        <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          {calledNumbers.map((number) => (
            <div
              key={number}
              className="bg-purple-600 text-white px-2 py-1 rounded text-sm"
            >
              {number}
            </div>
          ))}
        </div>
      </div>

      {/* Game Controls */}
      <div className="text-center">
        {isBingo ? (
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-6 mb-4">
            <div className="text-4xl mb-2">🎉</div>
            <div className="text-2xl font-bold text-white mb-2">BINGO!</div>
            <div className="text-white">Congratulations! You won!</div>
          </div>
        ) : null}
        
        <button
          onClick={() => {
            setGameStarted(false);
            setBingoCard(null);
            setCalledNumbers([]);
            setCurrentNumber(null);
            setGameTime(0);
            setIsBingo(false);
          }}
          className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-lg transition-colors"
        >
          New Game
        </button>
      </div>
    </div>
  );
};

export default BingoGame;
