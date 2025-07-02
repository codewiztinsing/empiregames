import React, { useState, useEffect } from 'react';
import BingoCard from '../components/BingoCard';
import Caller from '../components/Caller';
import io from 'socket.io-client';
import { SocketContext } from '../contexts/socket';
import { useContext } from 'react';
import './main.css';

function PlayingBoard() {
  const socket = useContext(SocketContext);
  const [players, setPlayers] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [calledNumbers, setCalledNumbers] = useState([]);
  const [gameStatus, setGameStatus] = useState('waiting'); // waiting, playing, ended
  const [winner, setWinner] = useState(null);

  useEffect(() => {
    // Socket event listeners
    socket.on('playerRegistered', (player) => {
      setCurrentPlayer(player);
    });

    socket.on('gameUpdate', (gameState) => {
      setPlayers(gameState.players);
      setCalledNumbers(gameState.calledNumbers);
      setGameStatus(gameState.status);
    });

    socket.on('gameWon', (winningPlayer) => {
      setWinner(winningPlayer);
      setGameStatus('ended');
    });

    // Register player on load
    const playerName = prompt('Enter your name') || `Player ${Math.floor(Math.random() * 1000)}`;
    socket.emit('registerPlayer', playerName);

    return () => {
      socket.off('playerRegistered');
      socket.off('gameUpdate');
      socket.off('gameWon');
    };
  }, []);

  const startGame = () => {
    socket.emit('startGame');
  };

  const callNumber = () => {
    socket.emit('callNumber');
  };

  return (
    <div className="app">
      <h1>Multiplayer Bingo</h1>
      
      {gameStatus === 'waiting' && (
        <div>
          <p>Waiting for players... {players.length} joined</p>
       
            <button onClick={startGame}>Start Game</button>
          
        </div>
      )}

      {gameStatus === 'playing' && (
        <div>
          <Caller calledNumbers={calledNumbers} onCallNumber={callNumber} />
          <div className="players-container">
            {players.map(player => (
              <div key={player.id} className={`player-card ${currentPlayer && player.id === currentPlayer.id ? 'current-player' : ''}`}>
                <h3>{player.name} {player.hasBingo ? '(BINGO!)' : ''}</h3>
                <BingoCard 
                  card={player.card} 
                  calledNumbers={calledNumbers} 
                  onBingo={() => socket.emit('declareBingo')}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {gameStatus === 'ended' && (
        <div>
          <h2>Game Over!</h2>
          {winner && <p>Winner: {winner.name}</p>}
          <button onClick={startGame}>Play Again</button>
        </div>
      )}
    </div>
  );
}

export default PlayingBoard;