import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BingoContext } from '../contexts/bingoContext';
import { SocketContext } from '../contexts/socket';
import './landing.css';

const Landing = () => {
  const { roomId,playerId,setPlayerId,setRoomId} = useContext(BingoContext);
  const navigate = useNavigate();
  const location = useLocation();
  const socket = useContext(SocketContext);
  const [activeGames, setActiveGames] = useState([]);
  // const [rooms, setRooms] = useState([
  //   { stake: 10, players: 175, balance: '88 ETB', isActive: true },
  //   { stake: 20, players: 28, balance: '448 ETB', isActive: true, lowBalance: true },
  //   { stake: 50, players: 8, balance: '0 ETB', lowBalance: true },
  //   { stake: 100, players: 20, balance: '1600 ETB', isActive: true, lowBalance: true }
  // ]);


  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const playerId = searchParams.get('playerId');
    const betAmount = searchParams.get('betAmount') || 10;
    setPlayerId(playerId);
    setRoomId(roomId);


    socket.on("activeGames",(state) => {
      console.log("active games ",state.activeGames[0])
      setActiveGames(state.activeGames)
    })

  
  

 
  }, [location.search, navigate,playerId,roomId]);

  

  const handlePlay = (stake) => {
    if(playerId){
      navigate(`/selection?playerId=${playerId}&betAmount=${stake}`);
    }
  };




  return (
    <div className="landing-container">
      {activeGames.map((room, index) => (
        <div key={index} className="room-row">
          <div className="stake-badge">
            <span>{room.stake}</span>
          </div>
          
          <div className="room-info">
            {room.roomId == room.roomId && <div className="active-badge">Active game 1</div>}
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
