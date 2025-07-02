import React, { createContext, useEffect } from 'react';
import socket from '../socket';

export const SocketContext = createContext();

export const SocketProvider = ({ children }) => {
  useEffect(() => {
    socket.connect(); // connect on mount

    return () => {
      socket.disconnect(); // disconnect only when app is fully unmounted
    };
  }, []);

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  );
};
