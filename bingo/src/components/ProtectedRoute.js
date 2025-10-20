import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, fallback = null, requireDeposit = false }) => {
  const { isAuthenticated, isLoading, user, checkDepositStatus } = useAuth();
  const [hasDeposit, setHasDeposit] = React.useState(null);

  React.useEffect(() => {
    if (requireDeposit && isAuthenticated && user) {
      checkDepositStatus().then(setHasDeposit);
    }
  }, [requireDeposit, isAuthenticated, user, checkDepositStatus]);

  // Show loading state
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  // Check authentication
  if (!isAuthenticated) {
    return fallback || (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        padding: '20px',
        textAlign: 'center'
      }}>
        <h2>Authentication Required</h2>
        <p>Please log in to access this page.</p>
        <button 
          onClick={() => window.location.reload()}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Login
        </button>
      </div>
    );
  }

  // Check deposit requirement
  if (requireDeposit && hasDeposit === false) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        padding: '20px',
        textAlign: 'center'
      }}>
        <h2>Deposit Required</h2>
        <p>You need to make a deposit to access this feature.</p>
        <button 
          onClick={() => window.location.href = '/profile'}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Go to Profile
        </button>
      </div>
    );
  }

  // Show loading for deposit check
  if (requireDeposit && hasDeposit === null) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#666'
      }}>
        Checking deposit status...
      </div>
    );
  }

  // All checks passed, render children
  return children;
};

export default ProtectedRoute;
