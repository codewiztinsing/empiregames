import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';
import Landing from './screens/landing';
import Profile from './screens/Profile';
import Transactions from './screens/Transactions';
import InvitedUsers from './screens/InvitedUsers';
import ReferralDashboard from './components/ReferralDashboard';
import ReferralCodeInput from './components/ReferralCodeInput';
import ReferralLanding from './components/ReferralLanding';
function App() {
  return (
    <BingoProvider>
      <Router>
        <Routes>
          <Route path="/play" element={<PlayingBoard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/invited-users" element={<InvitedUsers />} />
          <Route path="/" element={<SelectionScreen />} />
        </Routes>
      </Router>
    </BingoProvider>
  );
}

export default App;