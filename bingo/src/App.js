import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';
import Landing from './screens/landing';
import ReferralDashboard from './components/ReferralDashboard';
import ReferralCodeInput from './components/ReferralCodeInput';
import ReferralLanding from './components/ReferralLanding';
function App() {
  return (
    <BingoProvider>
      <Router>
        <Routes>
          <Route path="/play" element={<PlayingBoard />} />
          {/* <Route path="/referrals" element={<ReferralDashboard />} /> */}
          {/* <Route path="/referral-setup" element={<ReferralCodeInput />} /> */}
          <Route path="/" element={<SelectionScreen />} />
          {/* <Route path="/" element={<ReferralLanding />} /> */}
          {/* <Route path="/" element={<Landing />} /> */}
        </Routes>
      </Router>
    </BingoProvider>
  );
}

export default App;