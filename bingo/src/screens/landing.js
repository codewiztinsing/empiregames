import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import axios from 'axios';
import './landing.css';

const Landing = () => {
  // Initialize with empty rooms - all data will come from server
  const [rooms, setRooms] = useState([]);
  const [playerId, setPlayerId] = useState('');
  const [roomId, setRoomId] = useState('');
  const [globalCountdown, setGlobalCountdown] = useState(30);
  const [lastCalledNumber, setLastCalledNumber] = useState(null);
  const [totalPlayersOnline, setTotalPlayersOnline] = useState(0);
  const [totalGamesPlayed, setTotalGamesPlayed] = useState(0);
  const [totalWinnings, setTotalWinnings] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // API base URL
  const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

  // Fetch rooms from backend
  const fetchRooms = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/game/game-types/`);
      console.log("Fetched game types:", response.data);
      
      if (response.data && response.data.game_types) {
        // Transform API data to room format
        const fetchedRooms = response.data.game_types.map(gameType => ({
          betAmount: gameType.bet_amount,
          status: 'waiting',
          players: 0,
          countdown: 30,
          lastCalled: null,
          totalPot: 0,
          gamesPlayed: 0,
          avgPlayers: 0,
          commission: gameType.commission
        }));
        
        console.log("Transformed rooms:", fetchedRooms);
        setRooms(fetchedRooms);
      }
    } catch (err) {
      console.error("Error fetching rooms:", err);
      setError("Failed to load rooms. Using default rooms.");
      
      // Fallback to default rooms on error
      const defaultRooms = [
        { betAmount: 10, status: 'waiting', players: 0, countdown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 20, status: 'waiting', players: 0, countdown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 50, status: 'waiting', players: 0, countdown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 100, status: 'waiting', players: 0, countdown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 }
      ];
      setRooms(defaultRooms);
    } finally {
      setLoading(false);
    }
  };

  // Memoized handler to prevent unnecessary recreations
  const handleWaitingGames = useCallback((data) => {
    console.log("handleWaitingGames received:", data);
    if (data?.length > 0) {
      console.log("waiting games = ", data);
      
      setRooms(prevRooms => 
        prevRooms.map(room => {
          const matchingRoom = data.find(newRoom => 
            Number(newRoom.betAmount) === Number(room.betAmount)
          );
          
          if (matchingRoom) {
            return {
              ...room,
              status: room.betAmount < Number(roomId) ? 'Low balance' : matchingRoom.status,
              players: matchingRoom.players
            };
          }
          return room;
        })
      );
    }
  }, [roomId]);





  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const roomIdParam = queryParams.get('roomId');
    const playerIdParam = queryParams.get('playerId');
    
    if (roomIdParam) setRoomId(roomIdParam);
    if (playerIdParam) setPlayerId(playerIdParam);

    // Fetch rooms from backend
    fetchRooms();

    // Request initial data from server
    socket.emit("getAllRooms");
    
    // Listen for all rooms data from server
    socket.on("allRoomsData", (roomsData) => {
      console.log("Received rooms data:", roomsData);
      
      setRooms(prevRooms => 
        prevRooms.map(room => {
          const matchingRoom = roomsData.find(serverRoom => 
            Number(serverRoom.roomId) === Number(room.betAmount)
          );
          
          if (matchingRoom) {
            return {
              ...room,
              status: room.betAmount < Number(roomId) ? 'Low balance' : matchingRoom.gameStatus,
              players: matchingRoom.playersCount,
              countdown: matchingRoom.countDown,
              totalPot: matchingRoom.totalWinAmount
            };
          }
          return room;
        })
      );
    });
    
    socket.on("waitingGames", handleWaitingGames);
    
    // Listen for global game updates
    socket.on("globals", (data) => {
      console.log("Received globals:", data);
      if (data.countDown !== undefined) {
        setGlobalCountdown(data.countDown);
      }
      if (data.lastBall) {
        setLastCalledNumber(data.lastBall);
      }
      if (data.totalPlayers !== undefined) {
        setTotalPlayersOnline(data.totalPlayers);
      }
      if (data.totalGamesPlayed !== undefined) {
        setTotalGamesPlayed(data.totalGamesPlayed);
      }
      if (data.totalWinnings !== undefined) {
        setTotalWinnings(data.totalWinnings);
      }
    });

    // Listen for global stats updates
    socket.on("globalStats", (stats) => {
      console.log("Received globalStats:", stats);
      setTotalPlayersOnline(stats.totalPlayersOnline || 0);
      setTotalGamesPlayed(stats.totalGamesPlayed || 0);
      setTotalWinnings(stats.totalWinnings || 0);
      setLastCalledNumber(stats.lastCalledNumber || null);
      setGlobalCountdown(stats.globalCountdown || 30);
    });

    // Listen for game state updates
    socket.on("gameState", (gameState) => {
      console.log("Received gameState:", gameState);
      if (gameState.count_down !== undefined) {
        setGlobalCountdown(gameState.count_down);
        
        // Update room-specific data
        setRooms(prevRooms => 
          prevRooms.map(room => 
            room.betAmount === gameState.roomId 
              ? { 
                  ...room, 
                  countdown: gameState.count_down,
                  lastCalled: gameState.lastBall,
                  totalPot: gameState.win_amount || room.totalPot,
                  players: gameState.total_players || room.players
                }
              : room
          )
        );
      }
    });

    // Listen for room updates from server
    socket.on("roomUpdate", (roomData) => {
      console.log("Received roomUpdate:", roomData);
      setRooms(prevRooms => 
        prevRooms.map(room => 
          room.betAmount === roomData.roomId 
            ? { 
                ...room, 
                countdown: roomData.countDown,
                players: roomData.playersCount,
                status: roomData.gameStatus,
                totalPot: roomData.totalWinAmount
              }
            : room
        )
      );
    });
  
    return () => {
      socket.off('allRoomsData');
      socket.off('waitingGames', handleWaitingGames);
      socket.off('globals');
      socket.off('globalStats');
      socket.off('gameState');
      socket.off('roomUpdate');
    };
  }, [socket, handleWaitingGames]);

  const handleRoomSelect = (betAmount) => {
    const selectedRoom = rooms.find(room => room.betAmount === betAmount);
    
    if (selectedRoom?.status === 'in-progress') {
      alert('Game is already in progress');
      return;
    }
    
    if (selectedRoom?.status === 'Low balance') {
      alert('Your balance is too low for this room');
      return;
    }

    navigate(`/selection?betAmount=${betAmount}&playerId=${playerId}`);
  };

  // Show loading state
  if (loading) {
    return (
      <div className='landing-container'>
        <div className='loading-container'>
          <div className='loading-spinner'></div>
          <p>Loading rooms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className='landing-container'>
      {error && (
        <div className='error-message'>
          <p>{error}</p>
        </div>
      )}
    
      {/* Live Stats Section */}
      <div className='live-stats-container'>
        <div className='stat-card'>
          <div className='stat-icon'>⏱️</div>
          <div className='stat-content'>
            <div className='stat-value'>{globalCountdown.toString().padStart(2, '0')}s</div>
            <div className='stat-label'>Next Game</div>
          </div>
        </div>
        
        <div className='stat-card'>
          <div className='stat-icon'>🎯</div>
          <div className='stat-content'>
            <div className='stat-value'>{lastCalledNumber ? lastCalledNumber.number : '--'}</div>
            <div className='stat-label'>Last Called</div>
          </div>
        </div>
        
        <div className='stat-card'>
          <div className='stat-icon'>👥</div>
          <div className='stat-content'>
            <div className='stat-value'>{totalPlayersOnline}</div>
            <div className='stat-label'>Online</div>
          </div>
        </div>
        
        <div className='stat-card'>
          <div className='stat-icon'>🏆</div>
          <div className='stat-content'>
            <div className='stat-value'>{totalGamesPlayed.toLocaleString()}</div>
            <div className='stat-label'>Games Played</div>
          </div>
        </div>
      </div>

      <div className='rooms-container'>
        {rooms.map((room, index) => {
          const isDisabled = room.status === 'in-progress' || room.status === 'Low balance';
          
          // Different room themes based on bet amount
          const getRoomTheme = (betAmount) => {
            switch (betAmount) {
              case 10:
                return 'room-theme-bronze';
              case 20:
                return 'room-theme-silver';
              case 50:
                return 'room-theme-gold';
              case 100:
                return 'room-theme-platinum';
              default:
                return 'room-theme-default';
            }
          };
          
          return (
            <div key={room.betAmount} className={`room-card ${getRoomTheme(room.betAmount)}`}>
              {/* Room Title */}
              <div className='room-title'>
                <div className='room-title-left'>
                  <span className='room-bet-amount'>{room.betAmount} ETB</span>
                  {room.players > 0 && (
                    <span className='live-indicator'>
                      <span className='live-dot'></span>
                      LIVE
                    </span>
                  )}
                </div>
                <span className={`room-status ${room.status}`}>
                  {room.status === 'in-progress' && 'Active Game'}
                  {room.status === 'waiting' && 'Waiting'}
                  {room.status === 'Low balance' && 'Low Balance'}
                </span>
              </div>

              {/* Room Statistics - Horizontal Layout */}
              <div className='room-stats-horizontal'>
                <div className='room-stat-card'>
                  <div className='room-stat-icon'>👥</div>
                  <div className='room-stat-content'>
                    <span className='room-stat-value'>{room.players}</span>
                    <span className='room-stat-label'>Players</span>
                  </div>
                </div>
                
                <div className='room-stat-card'>
                  <div className='room-stat-icon'>💰</div>
                  <div className='room-stat-content'>
                    <span className='room-stat-value'>{(room.betAmount * room.players * 0.8).toLocaleString()}</span>
                    <span className='room-stat-label'>Pot</span>
                  </div>
                </div>
                
                <div className='room-stat-card'>
                  <div className='room-stat-icon'>⏱️</div>
                  <div className='room-stat-content'>
                    <span className='room-stat-value'>
                      {room.status === 'in-progress' ? room.countdown.toString().padStart(2, '0') + 's' : globalCountdown.toString().padStart(2, '0') + 's'}
                    </span>
                    <span className='room-stat-label'>Countdown</span>
                  </div>
                </div>
                
                <div className='room-stat-card'>
                  <div className='room-stat-icon'>🎯</div>
                  <div className='room-stat-content'>
                    <span className='room-stat-value'>
                      {room.lastCalled ? room.lastCalled.number : (lastCalledNumber ? lastCalledNumber.number : '--')}
                    </span>
                    <span className='room-stat-label'>Last</span>
                  </div>
                </div>
              </div>

              {/* Play Button */}
              <div className='room-action'>
                <button
                  onClick={() => handleRoomSelect(room.betAmount)}
                  className='play-button'
                  disabled={isDisabled}
                >
                  {room.players === 0 && room.status === 'waiting' ? (
                    <span className='waiting-text'>
                      <span className='waiting-dots'>•••</span> Waiting
                    </span>
                  ) : (
                    'Play'
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Landing;