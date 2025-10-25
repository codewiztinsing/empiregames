import React from 'react';
import './Spinner.css';

const Spinner = ({ message = "Please wait..." }) => {
  return (
    <div className="spinner-container">
      <div className="spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      <div className="spinner-message">{message}</div>
    </div>
  );
};

export default Spinner;
