import React from 'react';

function Caller({ calledNumbers, onCallNumber }) {
  return (
    <div className="caller">
      <h2>Called Numbers</h2>
      <div className="called-numbers">
        {calledNumbers.map((number, index) => (
          <span key={index} className="called-number">{number}</span>
        ))}
      </div>
      <button onClick={onCallNumber}>Call Next Number</button>
    </div>
  );
}

export default Caller;