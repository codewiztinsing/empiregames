import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';
import { LocalizationProvider } from './contexts/LocalizationContext';
import './i18n'; // Initialize i18n

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
    <LocalizationProvider>
      <BingoProvider>
        <Router>
          <Routes>
            <Route path="/play" element={<PlayingBoard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/invited-users" element={<InvitedUsers />} />
            <Route path="/referral-dashboard" element={<ReferralDashboard />} />
            <Route path="/referral-code" element={<ReferralCodeInput />} />
            <Route path="/referral-landing" element={<ReferralLanding />} />
            <Route path="/" element={<Landing />} />
            <Route path="/selections" element={<SelectionScreen />} />
          </Routes>
        </Router>
      </BingoProvider>
    </LocalizationProvider>
  );
}

export default App;