// src/contexts/MyContext.js (continued)
import { useState } from 'react';
import { createContext } from 'react';


export const BingoContext = createContext();

export const BingoProvider = ({ children }) => {
  const [state, setState] = useState({
    user: null,
    theme: 'light',
    isAuthenticated: false
  });

  const [selectedNumber, setSelectedNumber] = useState(null);
  const [selectBoard, setSelectBoard] = useState([]);
  const [playersLength, setPlayersLength] = useState(0);
  const [gameId, setGameId] = useState("1");


  // Any functions you want to expose
  const login = (userData) => {
    setState(prev => ({
      ...prev,
      user: userData,
      isAuthenticated: true
    }));
  };

  const logout = () => {
    setState(prev => ({
      ...prev,
      user: null,
      isAuthenticated: false
    }));
  };


  return (

    <BingoContext.Provider value={{ ...state, login,
     logout,
      selectedNumber,
       setSelectedNumber,
        selectBoard, 
        setSelectBoard, 
        gameId, 
        setGameId,
         playersLength, 
         setPlayersLength }}>
      {children}
    </BingoContext.Provider>
  );
};