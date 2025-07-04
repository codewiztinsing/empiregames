import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './landing.css';


const Landing = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [rooms, setRooms] = useState([
    { stake: 10, players: 175, balance: '88 ETB', isActive: true },
    { stake: 20, players: 28, balance: '448 ETB', isActive: true, lowBalance: true },
    { stake: 50, players: 8, balance: '0 ETB', lowBalance: true },
    { stake: 100, players: 20, balance: '1600 ETB', isActive: true, lowBalance: true }
  ]);

  const handlePlay = (stake) => {
    navigate(`/game?stake=${stake}`);
  };

  return (
    <div className="landing-container">
      {rooms.map((room, index) => (
        <div key={index} className="room-row">
          <div className="stake-badge">
            <span>{room.stake}</span>
          </div>
          
          <div className="room-info">
            {room.isActive && <div className="active-badge">Active game 1</div>}
            <div className={`balance-info ${room.lowBalance ? 'low-balance' : ''}`}>
              {room.lowBalance && <span>Low balance</span>}
              <span>{room.players}</span>
              <span>{room.balance}</span>
            </div>
          </div>

          <button 
            className={`play-button ${!room.isActive ? 'disabled' : ''}`}
            onClick={() => handlePlay(room.stake)}
            disabled={!room.isActive}
          >
            Play
          </button>
        </div>
      ))}
      
      <div className="footer">
        © Bilen bingo 2025
      </div>
    </div>
  );
};

export default Landing;
