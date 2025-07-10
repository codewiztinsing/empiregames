import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import './landing.css';

const Landing = () => {
  // Initial rooms data
  const initialRooms = [
    { id: 10, betAmount: 10, status: 'waiting', players: 0, bonus: 1 },
    { id: 20, betAmount: 20, status: 'waiting', players: 0, bonus: 1 },
    { id: 50, betAmount: 50, status: 'waiting', players: 0, bonus: 1 },
    { id: 100, betAmount: 100, status: 'waiting', players: 0, bonus: 1 }
  ];

  const [rooms, setRooms] = useState(initialRooms);
  const [playerId, setPlayerId] = useState('');
  const [roomId, setRoomId] = useState('');
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // Memoized handler to prevent unnecessary recreations
  const handleWaitingGames = useCallback((data) => {
    if (data?.length > 0) {
      console.log("waiting games = ", data);
      setRooms(prevRooms => 
        prevRooms.map(existingRoom => {
          const matchingRoom = data.find(newRoom => 
            Number(newRoom.betAmount) === Number(existingRoom.betAmount)
          );
          
          if (matchingRoom) {
            return {
              ...existingRoom,
              status: existingRoom.betAmount < Number(roomId) ? 'Low balance' : matchingRoom.status,
              players: matchingRoom.players
            };
          }
          return existingRoom;
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

    socket.on("waitingGames", handleWaitingGames);
    
    return () => {
      socket.off('waitingGames', handleWaitingGames);
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

  return (
    <div className='landing-container'>
      <div className='header'>
        <p>Stake</p>
        <p>Active</p>
        <p>Players</p>
        <p>Derash</p>
        <p>Play</p>
      </div>

      <div className='rooms-container'>
        {rooms.map(room => {
          const isDisabled = room.status === 'in-progress' || room.status === 'Low balance';
          
          return (
            <div key={room.betAmount} className='room-card'>
              <p className='room-card-bonus'>
                <span className='bonus'>Bonus</span>
                <span className='bet-amount'>{room.betAmount}</span>
              </p>
              <p className='room-card-status-container'>
                {room.status === 'in-progress' && (
                  <span className='room-card-active-game'>Active Game</span>
                )}
                {room.status === 'waiting' && (
                  <span className='room-card-active-game'>Waiting</span>
                )}
                {room.status === 'Low balance' && (
                  <span className='room-card-active-game'>Low balance</span>
                )}
              </p>
              <p>{room.players}</p>
              <p>{room.betAmount * room.players * 0.8} ETB</p>
              <button
                onClick={() => handleRoomSelect(room.betAmount)}
                className='play-button'
                disabled={isDisabled}
                style={{
                  backgroundColor: isDisabled ? 'gray' : 'blue',
                  cursor: isDisabled ? 'not-allowed' : 'pointer'
                }}
              >
                Play
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Landing;