import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import './landing.css';

const Landing = () => {
  const [rooms, setRooms] = useState([{
    id: 1,
    betAmount: 10,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 2,
    betAmount: 20,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 3,
    betAmount: 50,
    status: 'waiting',
    players: 0,
    bonus: 1
  },

  {
    id: 4,
    betAmount: 100,
    status: 'waiting',
    players: 0,
    bonus: 1
  }
  ])
  const [playerId, setPlayerId] = useState(0);  
 

  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const playerId = queryParams.get('playerId');
    setPlayerId(playerId);

    socket.on("waitingGames", (data) => {
      if (data.length > 0) {
        setRooms(data);
        console.log("rooms", rooms);
      }
    });
   
    return () => {
      socket.off('waitingGames');
    }
  }, [socket]);
  

  const handleRoomSelect = (roomId) => {
    navigate(`/selection?betAmount=${roomId}&playerId=${playerId}`);
  };


  socket.on("activeGames", (data) => {
    setRooms(data);
  });

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
          <div key={room.id} className='room-card' 
          onClick={() => handleRoomSelect(room.id)}>
            
            <p className='room-card-bonus'>
              <span className='bonus'>Bonus</span>
              <span className='bet-amount'>{room.betAmount}</span>
              
            </p>
            <p>{room.status}</p>
            <p>{room.players}</p>
            <p>{room.betAmount * room.players * 0.8} ETB</p>
            <p onClick={() => handleRoomSelect(room.id)} className='play-button'>Play</p>
          </div>
        ))}
       
      </div>
      
    </div>
  );
};

export default Landing;
