import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';
import { Toaster } from 'react-hot-toast';

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';
import Landing from './screens/landing';
import Dashboard from './screens/dashboard';
import Login from './screens/login';


function App() {
  return (
    <BingoProvider>
      <Router>
        <Routes>
          <Route path="/play" element={<PlayingBoard />} />
          <Route path="" element={<SelectionScreen />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </Router>
      <Toaster position="top-center" reverseOrder={false} />
    </BingoProvider>
  );
}

export default App;