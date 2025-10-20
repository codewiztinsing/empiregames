import React, { useState, useEffect } from 'react';
import { useTelegramAuth } from '../hooks/useTelegramAuth';
import telegramAuthService from '../services/telegramAuth';

const LoginScreen = ({ onLoginSuccess }) => {
  const { 
    isLoading, 
    error, 
    handleCompleteAuth, 
    showAlert, 
    isTelegram,
    platform,
    theme 
  } = useTelegramAuth();
  
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const handleLogin = async () => {
    setIsLoggingIn(true);
    
    try {
      const result = await handleCompleteAuth();
      
      if (result.success) {
        if (onLoginSuccess) {
          onLoginSuccess(result);
        }
      } else {
        showAlert(result.error || 'Login failed. Please try again.');
      }
    } catch (error) {
      console.error('Login error:', error);
      showAlert('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  // Auto-attempt login when component mounts
  useEffect(() => {
    if (isTelegram && !isLoggingIn) {
      handleLogin();
    }
  }, [isTelegram]);

  // Get theme colors
  const backgroundColor = theme?.bg_color || '#ffffff';
  const textColor = theme?.text_color || '#000000';
  const buttonColor = theme?.button_color || '#007bff';
  const buttonTextColor = theme?.button_text_color || '#ffffff';

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: backgroundColor,
      color: textColor,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        maxWidth: '400px',
        width: '100%',
        textAlign: 'center'
      }}>
        {/* Logo/Icon */}
        <div style={{
          fontSize: '64px',
          marginBottom: '20px'
        }}>
          🎮
        </div>

        {/* Title */}
        <h1 style={{
          fontSize: '28px',
          marginBottom: '10px',
          fontWeight: 'bold'
        }}>
          Welcome to Liyu Bingo
        </h1>

        {/* Subtitle */}
        <p style={{
          fontSize: '16px',
          marginBottom: '30px',
          opacity: 0.8,
          lineHeight: '1.5'
        }}>
          Play exciting bingo games and win amazing prizes!
        </p>

        {/* Platform Info */}
        {isTelegram && (
          <div style={{
            backgroundColor: 'rgba(0,0,0,0.1)',
            padding: '10px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            Running on {platform}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div style={{
            backgroundColor: '#f8d7da',
            color: '#721c24',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Login Button */}
        <button
          onClick={handleLogin}
          disabled={isLoading || isLoggingIn}
          style={{
            width: '100%',
            padding: '16px',
            fontSize: '18px',
            fontWeight: 'bold',
            backgroundColor: buttonColor,
            color: buttonTextColor,
            border: 'none',
            borderRadius: '12px',
            cursor: isLoading || isLoggingIn ? 'not-allowed' : 'pointer',
            opacity: isLoading || isLoggingIn ? 0.6 : 1,
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            marginBottom: '20px'
          }}
          onMouseOver={(e) => {
            if (!isLoading && !isLoggingIn) {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
            }
          }}
          onMouseOut={(e) => {
            if (!isLoading && !isLoggingIn) {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            }
          }}
        >
          {isLoading || isLoggingIn ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{
                width: '20px',
                height: '20px',
                border: '2px solid transparent',
                borderTop: '2px solid currentColor',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                marginRight: '10px'
              }}></div>
              {isLoading ? 'Initializing...' : 'Logging in...'}
            </div>
          ) : (
            'Login with Telegram'
          )}
        </button>

        {/* Features */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: '15px',
          marginTop: '30px'
        }}>
          <div style={{
            textAlign: 'center',
            padding: '15px',
            backgroundColor: 'rgba(0,0,0,0.05)',
            borderRadius: '8px'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎯</div>
            <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Easy to Play</div>
          </div>
          <div style={{
            textAlign: 'center',
            padding: '15px',
            backgroundColor: 'rgba(0,0,0,0.05)',
            borderRadius: '8px'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>💰</div>
            <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Win Prizes</div>
          </div>
          <div style={{
            textAlign: 'center',
            padding: '15px',
            backgroundColor: 'rgba(0,0,0,0.05)',
            borderRadius: '8px'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>👥</div>
            <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Refer Friends</div>
          </div>
        </div>

        {/* Instructions */}
        <div style={{
          marginTop: '30px',
          fontSize: '12px',
          opacity: 0.7,
          lineHeight: '1.4'
        }}>
          {!isTelegram ? (
            <p>⚠️ This app works best when opened from Telegram</p>
          ) : (
            <p>Tap the button above to start playing with your Telegram account</p>
          )}
        </div>
      </div>

      {/* Loading Animation Styles */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoginScreen;
