// src/hooks/useSocket.js
import { useContext } from 'react';
import { SocketContext } from '../contexts/socket';

export const useSocket = () => {
  const socket = useContext(SocketContext);
  
  if (!socket) {
    throw new Error('useSocket must be used within a SocketProvider');
  }

  return socket;
};