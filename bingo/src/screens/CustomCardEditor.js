import React, { useState, useEffect } from 'react';
import './CustomCardEditor.css';

const CustomCardEditor = ({ isOpen, onClose, onSave, userCustomCard = null }) => {
  const [cardName, setCardName] = useState('');
  const [cardNumbers, setCardNumbers] = useState({
    B: Array(5).fill(''),
    I: Array(5).fill(''),
    N: Array(5).fill(''),
    G: Array(5).fill(''),
    O: Array(5).fill('')
  });
  const [isDefault, setIsDefault] = useState(false);
  const [errors, setErrors] = useState({});

  // Column ranges
  const columnRanges = {
    B: { min: 1, max: 15 },
    I: { min: 16, max: 30 },
    N: { min: 31, max: 45 },
    G: { min: 46, max: 60 },
    O: { min: 61, max: 75 }
  };

  // Load existing custom card if provided
  useEffect(() => {
    if (userCustomCard) {
      setCardName(userCustomCard.name || '');
      setCardNumbers(userCustomCard.numbers || {
        B: Array(5).fill(''),
        I: Array(5).fill(''),
        N: Array(5).fill(''),
        G: Array(5).fill(''),
        O: Array(5).fill('')
      });
    }
  }, [userCustomCard]);

  // Generate random numbers for a column
  const generateRandomColumn = (column) => {
    const range = columnRanges[column];
    const numbers = [];
    const usedNumbers = new Set();
    
    for (let i = 0; i < 5; i++) {
      let randomNum;
      do {
        randomNum = Math.floor(Math.random() * (range.max - range.min + 1)) + range.min;
      } while (usedNumbers.has(randomNum));
      
      usedNumbers.add(randomNum);
      numbers.push(randomNum);
    }
    
    return numbers.sort((a, b) => a - b);
  };

  // Generate random card
  const generateRandomCard = () => {
    const newCardNumbers = {};
    Object.keys(columnRanges).forEach(column => {
      newCardNumbers[column] = generateRandomColumn(column);
    });
    setCardNumbers(newCardNumbers);
    setErrors({});
  };

  // Validate number input
  const validateNumber = (value, column) => {
    const range = columnRanges[column];
    const num = parseInt(value);
    
    if (value === '') return true; // Empty is allowed
    if (isNaN(num)) return false;
    if (num < range.min || num > range.max) return false;
    
    return true;
  };

  // Handle number input change
  const handleNumberChange = (column, index, value) => {
    if (value === '' || validateNumber(value, column)) {
      const newCardNumbers = { ...cardNumbers };
      newCardNumbers[column][index] = value;
      setCardNumbers(newCardNumbers);
      
      // Clear error for this field
      const errorKey = `${column}-${index}`;
      if (errors[errorKey]) {
        const newErrors = { ...errors };
        delete newErrors[errorKey];
        setErrors(newErrors);
      }
    }
  };

  // Validate entire card
  const validateCard = () => {
    const newErrors = {};
    const usedNumbers = new Set();
    
    Object.keys(columnRanges).forEach(column => {
      const range = columnRanges[column];
      
      for (let i = 0; i < 5; i++) {
        const value = cardNumbers[column][i];
        const errorKey = `${column}-${i}`;
        
        if (value === '') {
          newErrors[errorKey] = 'Number is required';
        } else {
          const num = parseInt(value);
          if (isNaN(num)) {
            newErrors[errorKey] = 'Invalid number';
          } else if (num < range.min || num > range.max) {
            newErrors[errorKey] = `Must be between ${range.min}-${range.max}`;
          } else if (usedNumbers.has(num)) {
            newErrors[errorKey] = 'Number already used';
          } else {
            usedNumbers.add(num);
          }
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle save
  const handleSave = () => {
    if (!cardName.trim()) {
      alert('Please enter a card name');
      return;
    }
    
    if (!validateCard()) {
      alert('Please fix all errors before saving');
      return;
    }
    
    const customCard = {
      name: cardName.trim(),
      numbers: cardNumbers,
      isDefault: isDefault,
      createdAt: new Date().toISOString()
    };
    
    onSave(customCard);
    onClose();
  };

  // Handle close
  const handleClose = () => {
    setCardName('');
    setCardNumbers({
      B: Array(5).fill(''),
      I: Array(5).fill(''),
      N: Array(5).fill(''),
      G: Array(5).fill(''),
      O: Array(5).fill('')
    });
    setErrors({});
    setIsDefault(false);
    onClose();
  };

  if (!isOpen) return null;

  console.log('CustomCardEditor rendering with isOpen:', isOpen);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(255, 0, 0, 0.9)',
      zIndex: 99999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        backgroundColor: 'yellow',
        padding: '50px',
        borderRadius: '20px',
        minWidth: '400px',
        minHeight: '300px',
        border: '5px solid blue'
      }}>
        <h1 style={{color: 'red', fontSize: '24px'}}>CUSTOM CARD EDITOR</h1>
        <button 
          onClick={handleClose}
          style={{
            backgroundColor: 'red',
            color: 'white',
            padding: '10px 20px',
            fontSize: '16px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          CLOSE MODAL
        </button>
        <p style={{fontSize: '18px', color: 'blue'}}>This modal is working!</p>
      </div>
    </div>
  );
};

export default CustomCardEditor;
