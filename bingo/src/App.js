import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';
import Landing from './screens/landing';
function App() {
  return (
    <BingoProvider>
      <Router>
        <Routes>
          <Route path="/play" element={<PlayingBoard />} />
          <Route path="/selection" element={<SelectionScreen />} />
          <Route path="/" element={<Landing />} />
        </Routes>
      </Router>
    </BingoProvider>
  );
}

export default App;