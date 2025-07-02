import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';

function App() {
  return (
    <BingoProvider>
      <Router>
        <Routes>
          <Route path="/play" element={<PlayingBoard />} />
          <Route path="/" element={<SelectionScreen />} />
        </Routes>
      </Router>
    </BingoProvider>
  );
}

export default App;