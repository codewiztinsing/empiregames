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
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // Fetch rooms from backend
  const fetchRooms = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}game/game-types/`);
      console.log("Fetched game types:", response.data);
      
      if (response.data && response.data.game_types) {
        // Transform API data to room format
        const fetchedRooms = response.data.game_types.map(gameType => ({
          betAmount: gameType.bet_amount,
          status: 'waiting',
          players: 0,
          roomCountDown: 30, // Use the same countdown as server (30 seconds)
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
        { betAmount: 10, status: 'waiting', players: 0, roomCountDown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 20, status: 'waiting', players: 0, roomCountDown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 50, status: 'waiting', players: 0, roomCountDown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 },
        { betAmount: 100, status: 'waiting', players: 0, roomCountDown: 30, lastCalled: null, totalPot: 0, gamesPlayed: 0, avgPlayers: 0 }
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
              roomCountDown: matchingRoom.roomCountDown || matchingRoom.countDown, // Use roomCountDown if available, fallback to countDown
              totalPot: matchingRoom.totalWinAmount,
              lastCalled: matchingRoom.pickedNumbers && matchingRoom.pickedNumbers.length > 0 
                ? { number: matchingRoom.pickedNumbers[matchingRoom.pickedNumbers.length - 1] }
                : room.lastCalled
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
      
      // Update room's lastCalled if we have roomId and lastBall
      if (data.roomId && data.lastBall) {
        setRooms(prevRooms => 
          prevRooms.map(room => {
            if (Number(room.betAmount) === Number(data.roomId)) {
              console.log(`Updating room ${room.betAmount} lastCalled from globals:`, data.lastBall);
              return {
                ...room,
                lastCalled: data.lastBall,
                // Also update other room data from globals
                players: data.totalPlayers || room.players,
                totalPot: data.totalWinAmount || room.totalPot
                // Don't override countdown here - let it come from other events
              };
            }
            return room;
          })
        );
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
        console.log("GameState for room:", gameState.roomId, "countdown:", gameState.count_down, "pickedNumbers:", gameState.pickedNumbers);
        // Update only the specific room, not global countdown
        setRooms(prevRooms => 
          prevRooms.map(room => {
            if (Number(room.betAmount) === Number(gameState.roomId)) {
              // Handle lastCalled data properly
              let newLastCalled = room.lastCalled;
              if (gameState.pickedNumbers && gameState.pickedNumbers.length > 0) {
                const lastNumber = gameState.pickedNumbers[gameState.pickedNumbers.length - 1];
                if (typeof lastNumber === 'object' && lastNumber.combined) {
                  newLastCalled = lastNumber;
                } else {
                  newLastCalled = { number: lastNumber };
                }
              } else if (gameState.lastBall) {
                newLastCalled = gameState.lastBall;
              }
              
              // Use the actual countdown from server
              const countdown = gameState.count_down;
              
              const updatedRoom = { 
                ...room, 
                roomCountDown: countdown,
                lastCalled: newLastCalled,
                totalPot: gameState.win_amount || gameState.totalWinAmount || room.totalPot,
                players: gameState.total_players || room.players
              };
              console.log("GameState updated room:", room.betAmount, "roomCountDown:", updatedRoom.roomCountDown, "lastCalled:", updatedRoom.lastCalled);
              return updatedRoom;
            }
            return room;
          })
        );
      }
    });

    // Listen for game status updates
    socket.on("gameStatus", (gameStatus) => {
      console.log("Received gameStatus:", gameStatus);
      if (gameStatus.status === 'waiting') {
        // Reset room to waiting state when game ends
        setRooms(prevRooms => 
          prevRooms.map(room => 
            Number(room.betAmount) === Number(gameStatus.roomId) 
                ? { 
                    ...room, 
                    status: 'waiting',
                    players: 0,
                    roomCountDown: 30,
                    lastCalled: null,
                    totalPot: 0
                  }
              : room
          )
        );
      }
    });

    // Listen for room updates from server
    socket.on("roomUpdate", (roomData) => {
      console.log("Received roomUpdate:", roomData);
      console.log("Room ID:", roomData.roomId, "RoomCountDown:", roomData.roomCountDown, "PickedNumbers:", roomData.pickedNumbers);
      console.log("Last called from pickedNumbers:", roomData.pickedNumbers && roomData.pickedNumbers.length > 0 ? roomData.pickedNumbers[roomData.pickedNumbers.length - 1] : "none");
      console.log("Full roomData object:", JSON.stringify(roomData, null, 2));
      setRooms(prevRooms => {
        console.log("Previous rooms before update:", prevRooms);
        return prevRooms.map(room => {
          console.log("Checking room:", room.betAmount, "against roomData.roomId:", roomData.roomId);
          if (Number(room.betAmount) === Number(roomData.roomId)) {
            console.log("Current room lastCalled before update:", room.lastCalled);
            
            // Handle lastCalled data properly
            let newLastCalled = room.lastCalled;
            if (roomData.pickedNumbers && roomData.pickedNumbers.length > 0) {
              const lastNumber = roomData.pickedNumbers[roomData.pickedNumbers.length - 1];
              // Handle different data structures for lastCalled
              if (typeof lastNumber === 'object' && lastNumber.combined) {
                newLastCalled = lastNumber; // Use the full object with combined property
              } else {
                newLastCalled = { number: lastNumber };
              }
            }
            console.log("New lastCalled value:", newLastCalled);
            
            // Use the actual countdown from server
            const countdown = roomData.roomCountDown || roomData.countDown || 30;
            
            const updatedRoom = { 
              ...room, 
              roomCountDown: countdown,
              players: roomData.playersCount || room.players,
              status: roomData.gameStatus || room.status,
              totalPot: roomData.totalWinAmount || room.totalPot,
              lastCalled: newLastCalled
            };
            console.log("Updated room:", room.betAmount, "with roomCountDown:", updatedRoom.roomCountDown, "lastCalled:", updatedRoom.lastCalled);
            console.log("Full updatedRoom object:", JSON.stringify(updatedRoom, null, 2));
            return updatedRoom;
          }
          return room;
        });
      });
      console.log("Rooms updated, new rooms state should be visible in next render");
    });
  
    return () => {
      socket.off('allRoomsData');
      socket.off('waitingGames', handleWaitingGames);
      socket.off('globals');
      socket.off('globalStats');
      socket.off('gameState');
      socket.off('gameStatus');
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
      {/* <div className='live-stats-container'>
        <div className='stat-card'>
          <div className='stat-icon'>⏱️</div>
          <div className='stat-content'>
            <div className='stat-value'>{globalCountdown.toString().padStart(2, '0')}s</div>
            <div className='stat-label'>Next Game</div>
          </div>
        </div>
        
      
        
        <div className='stat-card'>
          <div className='stat-icon'>👥</div>
          <div className='stat-content'>
            <div className='stat-value'>{totalPlayersOnline}</div>
            <div className='stat-label'>Online</div>
          </div>
        </div>
        
      
      </div> */}

      <div className='rooms-container'>
        {rooms.map((room, index) => {
          // Determine if room is active (game is running)
          // A room is active if it has a last called number
          const isActive = room.lastCalled && room.lastCalled !== null;
          const isDisabled = isActive || room.status === 'Low balance';
        
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
                <span className={`room-status ${isActive ? 'in-progress' : room.status}`}>
                  {isActive && 'Active'}
                  {!isActive && room.status === 'waiting' && 'Waiting'}
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
                  <div className='room-stat-icon'>⏱️</div>
                  <div className='room-stat-content'>
                      <span className='room-stat-value'>
                        {(room.roomCountDown || 30).toString().padStart(2, '0')}s
                      </span>
                    <span className='room-stat-label'>Countdown</span>
                  </div>
                </div>
                
                {/* Conditional rendering based on game state */}
                {(isActive || room.roomCountDown === 0) ? (
                  <div className='room-stat-card'>
                    <div className='room-stat-icon'>🎯</div>
                    <div className='room-stat-content'>
                      <span className='room-stat-value'>
                        {(() => {
                          console.log(`Room ${room.betAmount} lastCalled:`, room.lastCalled);
                          if (room.lastCalled) {
                            // Handle different data structures
                            if (room.lastCalled.combined) {
                              return room.lastCalled.combined; // e.g., "B-7"
                            } else if (room.lastCalled.number) {
                              return room.lastCalled.number;
                            } else if (typeof room.lastCalled === 'string') {
                              return room.lastCalled;
                            }
                          }
                          // If countdown is 0 but no last called number, show "Starting..."
                          if (room.roomCountDown === 0) {
                            return 'Starting...';
                          }
                          return '--';
                        })()}
                      </span>
                      <span className='room-stat-label'>Last</span>
                    </div>
                  </div>
                ) : (
                  <div className='room-stat-card play-button-stat'>
                    <button
                      onClick={() => handleRoomSelect(room.betAmount)}
                      className='play-button-small'
                      disabled={isDisabled}
                    >
                      {room.players === 0 && !isActive ? (
                        <span className='waiting-text-small'>
                          <span className='waiting-dots'>•••</span> Play
                        </span>
                      ) : (
                        'Play'
                      )}
                    </button>
                  </div>
                )}
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Landing;