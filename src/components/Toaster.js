import React, { useState, useEffect } from 'react';

const Toaster = ({ message, duration = 3000, type = 'info' }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration]);

  if (!isVisible) return null;

  const toasterStyles = {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    padding: '12px 24px',
    borderRadius: '4px',
    color: '#fff',
    fontSize: '16px',
    zIndex: 1000,
    animation: 'slideIn 0.3s ease-in-out',
    backgroundColor: type === 'success' ? '#4caf50' : 
                    type === 'error' ? '#f44336' :
                    type === 'warning' ? '#ff9800' : '#2196f3'
  };

  const keyframes = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `;

  return (
    <>
      <style>{keyframes}</style>
      <div style={toasterStyles}>
        {message}
      </div>
    </>
  );
};

export default Toaster;
