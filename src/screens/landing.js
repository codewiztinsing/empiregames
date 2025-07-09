import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import './landing.css';

const Landing = () => {
  const [rooms, setRooms] = useState([{
    id: 10,
    betAmount: 10,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 20,
    betAmount: 20,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 50,
    betAmount: 50,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 100,
    betAmount: 100,
    status: 'waiting',
    players: 0,
    bonus: 1
  }
  ])
  const [playerId, setPlayerId] = useState(0);  
  const [roomId, setRoomId] = useState(0);
 

  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const roomId = queryParams.get('roomId');
    setRoomId(roomId);
    
    const playerId = queryParams.get('playerId');
    setPlayerId(playerId);

    socket.on("waitingGames", handleWaitingGames);
   
    return () => {
      socket.off('waitingGames');
    }
  }, [socket,rooms]);
  

  const handleWaitingGames = (data) => {
   
    if (data.length > 0) {
      console.log("data in waiting games", data);
      const updatedRooms = rooms.map(
        
        existingRoom => {
        const matchingRoom = data.find(newRoom => {
          return newRoom.betAmount.toString() === existingRoom.betAmount.toString()
        });
        
        if (matchingRoom) {
          return {
            ...existingRoom,
            status: existingRoom.betAmount < roomId ? 'Low balance' : matchingRoom.status,
            players: matchingRoom.players
          };
        }
        return existingRoom;
      });
      
      setRooms(updatedRooms);
     
    
    }
  }

  const handleRoomSelect = (roomId) => {
    navigate(`/selection?betAmount=${roomId}&playerId=${playerId}`);
  };


  socket.on("waitingGames", handleWaitingGames);

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
        {rooms.map(room => (
          <div key={room.betAmount} className='room-card' 
          onClick={() => handleRoomSelect(room.betAmount)}>
            
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
            </p>
            <p>{room.players}</p>
            <p>{room.betAmount * room.players * 0.8} ETB</p>
            <p onClick={() => handleRoomSelect(room.id)} 
                className='play-button'
                disabled={room.status === 'in-progress' ? true : false}
                style={{
                  backgroundColor: room.status === 'in-progress' ? 'gray' : 'blue',
                  cursor: room.status === 'in-progress' ? 'not-allowed' : 'pointer'
                }}
            >Play</p>
          </div>
        ))}
       
      </div>
      
    </div>
  );
};

export default Landing;
