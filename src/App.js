import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/play" element={<PlayingBoard />} />
        <Route path="/" element={<SelectionScreen />} />
      </Routes>
    </Router>
  );
}

export default App;