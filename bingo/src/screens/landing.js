import React, { useState, useEffect, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { SocketContext } from '../contexts/socket';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGamepad, faUsers, faTrophy, faPlay } from '@fortawesome/free-solid-svg-icons';
import LanguageSelector from '../components/LanguageSelector';
import { useTranslation } from 'react-i18next';
import './landing.css';

const Landing = () => {
  const { t } = useTranslation();
  
  // Initial rooms data
  const initialRooms = [
    { id: 10, betAmount: 10, status: 'waiting', players: 0, bonus: 1 }
  ];

  const [rooms, setRooms] = useState(initialRooms);
  const [playerId, setPlayerId] = useState('');
  const [roomId, setRoomId] = useState('');
  const [totalPlayers, setTotalPlayers] = useState(0);
  const [totalPrize, setTotalPrize] = useState(0);
  const socket = useContext(SocketContext);
  const navigate = useNavigate();

  // Memoized handler to prevent unnecessary recreations
  const handleWaitingGames = useCallback((data) => {
    if (data?.length > 0) {
      console.log("waiting games = ", data);
      setRooms(prevRooms => {
        const updatedRooms = prevRooms.map(existingRoom => {
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
        });
        
        // Calculate totals
        const totalPlayersCount = updatedRooms.reduce((sum, room) => sum + room.players, 0);
        const totalPrizeAmount = updatedRooms.reduce((sum, room) => sum + (room.betAmount * room.players * 0.8), 0);
        
        setTotalPlayers(totalPlayersCount);
        setTotalPrize(totalPrizeAmount);
        
        return updatedRooms;
      });
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
    // Force betAmount to 10
    betAmount = 10;
    const selectedRoom = rooms.find(room => room.betAmount === 10);
    
    if (selectedRoom?.status === 'in-progress') {
      alert('Game is already in progress');
      return;
    }
    
    if (selectedRoom?.status === 'Low balance') {
      alert('Your balance is too low for this room');
      return;
    }

    navigate(`/selection?betAmount=10&playerId=${playerId}`);
  };

  return (
    <div className='landing-container'>
      {/* Enhanced Header */}
      <div className='header'>
        <div className='header-left'>
          <div className='logo'>L</div>
          <div className='header-title'>{t('game.title')}</div>
        </div>
        
        <div className='header-right'>
          <div className='header-stats'>
            <div className='stat-item'>
              <FontAwesomeIcon icon={faUsers} />
              <span>{totalPlayers}</span>
            </div>
            <div className='stat-item'>
              <FontAwesomeIcon icon={faTrophy} />
              <span>{totalPrize.toFixed(0)} ETB</span>
            </div>
          </div>
          <LanguageSelector />
        </div>
      </div>

      {/* Enhanced Rooms Container */}
      <div className='rooms-container'>
        {rooms.map(room => {
          const isDisabled = room.status === 'in-progress' || room.status === 'Low balance';
          
          return (
            <div key={room.betAmount} className='room-card'>
              <div className='room-card-bonus'>
                <div className='bonus'>{t('game.bonus')}</div>
                <div className='bet-amount'>{room.betAmount} ETB</div>
              </div>
              
              <div className='room-card-status-container'>
                {room.status === 'in-progress' && (
                  <div className='room-card-active-game in-progress'>{t('game.inProgress')}</div>
                )}
                {room.status === 'waiting' && (
                  <div className='room-card-active-game waiting'>{t('game.waiting')}</div>
                )}
                {room.status === 'Low balance' && (
                  <div className='room-card-active-game low-balance'>{t('game.lowBalance')}</div>
                )}
                <div className='players-count'>
                  <FontAwesomeIcon icon={faUsers} />
                  {room.players}
                </div>
              </div>
              
              <div className='prize-amount'>
                <FontAwesomeIcon icon={faTrophy} />
                {(room.betAmount * room.players * 0.8).toFixed(0)} ETB
              </div>
              
              <button
                onClick={() => handleRoomSelect(room.betAmount)}
                className='play-button'
                disabled={isDisabled}
              >
                <FontAwesomeIcon icon={faPlay} />
                {t('game.play')}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Landing;