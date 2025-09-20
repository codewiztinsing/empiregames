import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faUsers, faClock, faGamepad, faEye } from '@fortawesome/free-solid-svg-icons';
import { SocketContext } from '../contexts/socket';
import '../screens/rooms.css';

const RoomsOverview = () => {
  const navigate = useNavigate();
  const socket = useContext(SocketContext);
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Request all rooms data from server
    socket.emit('getAllRooms');
    
    // Listen for rooms data
    socket.on('allRoomsData', (roomsData) => {
      console.log('Received rooms data:', roomsData);
      setRooms(roomsData);
      setLoading(false);
    });

    // Listen for room updates
    socket.on('roomUpdate', (roomData) => {
      console.log('Room update received:', roomData);
      setRooms(prevRooms => {
        const updatedRooms = prevRooms.map(room => 
          room.roomId === roomData.roomId ? { ...room, ...roomData } : room
        );
        
        // If it's a new room, add it
        if (!prevRooms.find(room => room.roomId === roomData.roomId)) {
          updatedRooms.push(roomData);
        }
        
        return updatedRooms;
      });
    });

    // Listen for game state changes
    socket.on('gameState', (gameState) => {
      console.log('Game state update:', gameState);
      setRooms(prevRooms => 
        prevRooms.map(room => 
          room.roomId === gameState.roomId 
            ? { 
                ...room, 
                countDown: gameState.countDown,
                gameStatus: gameState.gameStatus,
                pickedNumbers: gameState.pickedNumbers?.numbers || [],
                playersCount: gameState.players ? gameState.players.size : 0
              }
            : room
        )
      );
    });

    // Listen for player joins/leaves
    socket.on('playerJoined', (data) => {
      console.log('Player joined:', data);
      setRooms(prevRooms => 
        prevRooms.map(room => 
          room.roomId === data.roomId 
            ? { ...room, playersCount: (room.playersCount || 0) + 1 }
            : room
        )
      );
    });

    socket.on('playerLeft', (data) => {
      console.log('Player left:', data);
      setRooms(prevRooms => 
        prevRooms.map(room => 
          room.roomId === data.roomId 
            ? { ...room, playersCount: Math.max(0, (room.playersCount || 0) - 1) }
            : room
        )
      );
    });

    return () => {
      socket.off('allRoomsData');
      socket.off('roomUpdate');
      socket.off('gameState');
      socket.off('playerJoined');
      socket.off('playerLeft');
    };
  }, [socket]);

  const formatCountdown = (countdown) => {
    if (countdown === null || countdown === undefined) return '--';
    return countdown.toString().padStart(2, '0');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'waiting': return '#f39c12';
      case 'in-progress': return '#e74c3c';
      case 'finished': return '#95a5a6';
      default: return '#3498db';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'waiting': return 'Waiting';
      case 'in-progress': return 'Playing';
      case 'finished': return 'Finished';
      default: return 'Unknown';
    }
  };

  const handleJoinRoom = (roomId) => {
    navigate(`/selection?roomId=${roomId}`);
  };

  if (loading) {
    return (
      <div className="rooms-container">
        <div className="rooms-header">
          <button className="back-button" onClick={() => navigate('/')}>
            <FontAwesomeIcon icon={faArrowLeft} />
          </button>
          <h1>Rooms Overview</h1>
        </div>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading rooms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rooms-container">
      <div className="rooms-header">
        <button className="back-button" onClick={() => navigate('/')}>
          <FontAwesomeIcon icon={faArrowLeft} />
        </button>
        <h1>Live Rooms</h1>
        <div className="refresh-info">
          <span>Real-time updates</span>
        </div>
      </div>

      <div className="rooms-grid">
        {rooms.length === 0 ? (
          <div className="no-rooms">
            <FontAwesomeIcon icon={faGamepad} size="3x" />
            <h3>No Active Rooms</h3>
            <p>No rooms are currently active</p>
          </div>
        ) : (
          rooms.map((room) => (
            <div key={room.roomId} className="room-card">
              <div className="room-header">
                <div className="room-id">Room {room.roomId}</div>
                <div 
                  className="room-status"
                  style={{ backgroundColor: getStatusColor(room.gameStatus) }}
                >
                  {getStatusText(room.gameStatus)}
                </div>
              </div>

              <div className="room-stats">
                <div className="stat-item">
                  <FontAwesomeIcon icon={faUsers} className="stat-icon" />
                  <div className="stat-content">
                    <span className="stat-value">{room.playersCount || 0}</span>
                    <span className="stat-label">Players</span>
                  </div>
                </div>

                <div className="stat-item">
                  <FontAwesomeIcon icon={faEye} className="stat-icon" />
                  <div className="stat-content">
                    <span className="stat-value">{room.pickedNumbers?.length || 0}</span>
                    <span className="stat-label">Called</span>
                  </div>
                </div>

                <div className="stat-item">
                  <FontAwesomeIcon icon={faClock} className="stat-icon" />
                  <div className="stat-content">
                    <span className="stat-value">{formatCountdown(room.countDown)}</span>
                    <span className="stat-label">Countdown</span>
                  </div>
                </div>
              </div>

              <div className="room-details">
                <div className="room-bet">
                  <span className="bet-label">Bet Amount:</span>
                  <span className="bet-value">{room.roomId} Birr</span>
                </div>
                
                {room.pickedNumbers && room.pickedNumbers.length > 0 && (
                  <div className="recent-numbers">
                    <span className="recent-label">Recent:</span>
                    <div className="numbers-list">
                      {room.pickedNumbers.slice(-5).map((num, index) => (
                        <span key={index} className="recent-number">{num}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="room-actions">
                <button 
                  className="join-room-btn"
                  onClick={() => handleJoinRoom(room.roomId)}
                  disabled={room.gameStatus === 'finished'}
                >
                  {room.gameStatus === 'finished' ? 'Game Over' : 'Join Room'}
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="rooms-footer">
        <p>Total Rooms: {rooms.length}</p>
        <p>Last Updated: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
};

export default RoomsOverview;
