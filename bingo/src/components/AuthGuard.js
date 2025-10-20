import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import telegramAuthService from '../services/telegramAuth';

const AuthGuard = ({ children, onAuthComplete, onAuthError }) => {
  const { isAuthenticated, isLoading, handleCompleteAuth, error } = useAuth();
  const [authAttempted, setAuthAttempted] = useState(false);

  useEffect(() => {
    const performAuth = async () => {
      if (authAttempted || isLoading) return;

      try {
        setAuthAttempted(true);

        // Check if we're in Telegram WebApp
        if (!telegramAuthService.isTelegram()) {
          console.warn('Not running in Telegram WebApp');
          if (onAuthError) {
            onAuthError('This app must be opened from Telegram');
          }
          return;
        }

        // If already authenticated, call onAuthComplete
        if (isAuthenticated) {
          if (onAuthComplete) {
            onAuthComplete();
          }
          return;
        }

        // Attempt authentication
        const result = await handleCompleteAuth();
        
        if (result.success) {
          if (onAuthComplete) {
            onAuthComplete();
          }
        } else {
          if (onAuthError) {
            onAuthError(result.error || 'Authentication failed');
          }
        }
      } catch (error) {
        console.error('AuthGuard error:', error);
        if (onAuthError) {
          onAuthError(error.message || 'Authentication error');
        }
      }
    };

    performAuth();
  }, [isAuthenticated, isLoading, authAttempted, handleCompleteAuth, onAuthComplete, onAuthError]);

  // Show loading while authenticating
  if (isLoading || !authAttempted) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f8f9fa',
        color: '#333'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #007bff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '20px'
        }}></div>
        <h3>Initializing...</h3>
        <p>Please wait while we set up your account</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Show error if authentication failed
  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        padding: '20px',
        backgroundColor: '#f8f9fa',
        color: '#333',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '48px',
          marginBottom: '20px'
        }}>⚠️</div>
        <h2>Authentication Error</h2>
        <p style={{ marginBottom: '20px' }}>{error}</p>
        <button 
          onClick={() => window.location.reload()}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  // Show children if authenticated
  if (isAuthenticated) {
    return children;
  }

  // Show waiting state
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: '#f8f9fa',
      color: '#333',
      textAlign: 'center'
    }}>
      <div style={{
        fontSize: '48px',
        marginBottom: '20px'
      }}>🔐</div>
      <h2>Authentication Required</h2>
      <p>Please complete authentication to continue</p>
    </div>
  );
};

export default AuthGuard;
