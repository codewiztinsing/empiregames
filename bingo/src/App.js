import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BingoProvider } from './contexts/bingoContext';
import { LocalizationProvider } from './contexts/LocalizationContext';
import { AuthProvider } from './contexts/AuthContext';
import './i18n'; // Initialize i18n

import PlayingBoard from './screens/main';
import SelectionScreen from './screens/selections';
import WatchModeScreen from './screens/watchMode';
import Landing from './screens/landing';
import Profile from './screens/Profile';
import Transactions from './screens/Transactions';
import InvitedUsers from './screens/InvitedUsers';
import ReferralDashboard from './components/ReferralDashboard';
import ReferralCodeInput from './components/ReferralCodeInput';
import ReferralLanding from './components/ReferralLanding';

// Import authentication components
import AuthGuard from './components/AuthGuard';
import LoginScreen from './components/LoginScreen';
import UserProfile from './components/UserProfile';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <LocalizationProvider>
      <AuthProvider>
        <BingoProvider>
          <Router>
            <AuthGuard
              onAuthComplete={() => console.log('Authentication completed')}
              onAuthError={(error) => console.error('Authentication error:', error)}
            >
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginScreen />} />
                
                {/* Protected routes */}
                <Route path="/play" element={
                  <ProtectedRoute>
                    <PlayingBoard />
                  </ProtectedRoute>
                } />
                <Route path="/watch" element={
                  <ProtectedRoute>
                    <WatchModeScreen />
                  </ProtectedRoute>
                } />
                <Route path="/profile" element={
                  <ProtectedRoute>
                    <UserProfile />
                  </ProtectedRoute>
                } />
                <Route path="/transactions" element={
                  <ProtectedRoute>
                    <Transactions />
                  </ProtectedRoute>
                } />
                <Route path="/invited-users" element={
                  <ProtectedRoute>
                    <InvitedUsers />
                  </ProtectedRoute>
                } />
                <Route path="/referral-dashboard" element={
                  <ProtectedRoute>
                    <ReferralDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/referral-code" element={
                  <ProtectedRoute>
                    <ReferralCodeInput />
                  </ProtectedRoute>
                } />
                <Route path="/referral-landing" element={
                  <ProtectedRoute>
                    <ReferralLanding />
                  </ProtectedRoute>
                } />
                
                {/* Legacy routes (keep for backward compatibility) */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <SelectionScreen />
                  </ProtectedRoute>
                } />
                
               
              </Routes>
            </AuthGuard>
          </Router>
        </BingoProvider>
      </AuthProvider>
    </LocalizationProvider>
  );
}

export default App;