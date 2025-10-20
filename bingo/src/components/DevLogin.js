import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const DevLogin = ({ onLogin }) => {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleDevLogin = async () => {
    setIsLoading(true);
    try {
      const result = await login();
      if (result.success && onLogin) {
        onLogin();
      }
    } catch (error) {
      console.error('Dev login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: '#f8f9fa',
      color: '#333',
      textAlign: 'center',
      padding: '20px'
    }}>
      <div style={{
        fontSize: '48px',
        marginBottom: '20px'
      }}>🛠️</div>
      
      <h2>Development Mode</h2>
      <p style={{ marginBottom: '30px', maxWidth: '400px' }}>
        Telegram authentication is bypassed in development mode. 
        Click the button below to login with mock user data.
      </p>
      
      <button 
        onClick={handleDevLogin}
        disabled={isLoading}
        style={{
          padding: '15px 30px',
          fontSize: '16px',
          backgroundColor: isLoading ? '#6c757d' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          transition: 'background-color 0.2s'
        }}
      >
        {isLoading ? 'Logging in...' : 'Login as Dev User'}
      </button>
      
      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#e9ecef',
        borderRadius: '8px',
        fontSize: '14px',
        maxWidth: '400px'
      }}>
        <strong>Mock User Data:</strong><br/>
        Username: dev_user<br/>
        Telegram ID: 123456789<br/>
        Phone: +251900000000
      </div>
    </div>
  );
};

export default DevLogin;
