import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft, faSave, faTrash, faEye, faEdit, faBars } from '@fortawesome/free-solid-svg-icons';
import { BingoContext } from '../contexts/bingoContext';
import { useAuth } from '../contexts/AuthContext';
import config from '../config/api';
import customCardsAPI from '../api/customCards';
import './CustomBoard.css';
import './selections.css';

const CustomBoard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { setToast, setIsToast } = useContext(BingoContext);
  
  // State for custom cards
  const [userCustomCards, setUserCustomCards] = useState([]);
  const [userDefaultCard, setUserDefaultCard] = useState(null);
  const [editingCard, setEditingCard] = useState(null);
  const [showCardManager, setShowCardManager] = useState(false);
  
  // State for card editor
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

  // Load existing custom card if editing
  useEffect(() => {
    if (editingCard) {
      setCardName(editingCard.name || '');
      setCardNumbers(editingCard.numbers || {
        B: Array(5).fill(''),
        I: Array(5).fill(''),
        N: Array(5).fill(''),
        G: Array(5).fill(''),
        O: Array(5).fill('')
      });
      setIsDefault(editingCard.is_default || false);
    } else {
      setCardName('');
      setCardNumbers({
        B: Array(5).fill(''),
        I: Array(5).fill(''),
        N: Array(5).fill(''),
        G: Array(5).fill(''),
        O: Array(5).fill('')
      });
      setIsDefault(false);
    }
    setErrors({});
  }, [editingCard]);

  // API Functions
  const fetchUserCustomCards = async () => {
    if (!user?.telegram_id) return;
    
    try {
      const cards = await customCardsAPI.getUserCustomCards(user.telegram_id);
      setUserCustomCards(cards);
    } catch (error) {
      console.error('Error fetching custom cards:', error);
    }
  };

  const fetchUserDefaultCard = async () => {
    if (!user?.telegram_id) return;
    
    try {
      const defaultCard = await customCardsAPI.getUserDefaultCard(user.telegram_id);
      setUserDefaultCard(defaultCard);
    } catch (error) {
      console.error('Error fetching default card:', error);
    }
  };

  const saveCustomCard = async () => {
    if (!user?.telegram_id) return;
    
    if (!cardName.trim()) {
      setToast('Please enter a card name');
      setIsToast(true);
      return;
    }
    
    if (!validateCard()) {
      setToast('Please fix all errors before saving');
      setIsToast(true);
      return;
    }
    
    try {
      const url = editingCard 
        ? `${config.API_BASE_URL}game/custom-cards/${editingCard.id}/`
        : `${config.API_BASE_URL}game/custom-cards/create/`;
      
      const method = editingCard ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_id: user.telegram_id,
          name: cardName.trim(),
          numbers: cardNumbers,
          is_default: isDefault
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setToast(`✅ Custom card "${cardName}" ${editingCard ? 'updated' : 'saved'} successfully!`);
        setIsToast(true);
        fetchUserCustomCards();
        fetchUserDefaultCard();
        setEditingCard(null);
        resetForm();
      } else {
        const error = await response.json();
        setToast(`❌ Error: ${error.error}`);
        setIsToast(true);
      }
    } catch (error) {
      console.error('Error saving custom card:', error);
      setToast('❌ Error saving custom card');
      setIsToast(true);
    }
  };

  const deleteCustomCard = async (cardId) => {
    if (!user?.telegram_id) return;
    
    try {
      const response = await fetch(`${config.API_BASE_URL}/game/custom-cards/${cardId}/?telegram_id=${user.telegram_id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const data = await response.json();
        setToast(`✅ ${data.message}`);
        setIsToast(true);
        fetchUserCustomCards();
        fetchUserDefaultCard();
      } else {
        const error = await response.json();
        setToast(`❌ Error: ${error.error}`);
        setIsToast(true);
      }
    } catch (error) {
      console.error('Error deleting custom card:', error);
      setToast('❌ Error deleting custom card');
      setIsToast(true);
    }
  };

  const setDefaultCard = async (cardId) => {
    if (!user?.telegram_id) return;
    
    try {
      const response = await fetch(`${config.API_BASE_URL}/game/custom-cards/${cardId}/set-default/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_id: user.telegram_id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setToast(`✅ ${data.message}`);
        setIsToast(true);
        fetchUserCustomCards();
        fetchUserDefaultCard();
      } else {
        const error = await response.json();
        setToast(`❌ Error: ${error.error}`);
        setIsToast(true);
      }
    } catch (error) {
      console.error('Error setting default card:', error);
      setToast('❌ Error setting default card');
      setIsToast(true);
    }
  };

  // Card generation and validation functions
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

  const generateRandomCard = () => {
    const newCardNumbers = {};
    Object.keys(columnRanges).forEach(column => {
      newCardNumbers[column] = generateRandomColumn(column);
    });
    setCardNumbers(newCardNumbers);
    setErrors({});
  };

  const validateNumber = (value, column) => {
    const range = columnRanges[column];
    const num = parseInt(value);
    
    if (value === '') return true;
    if (isNaN(num)) return false;
    if (num < range.min || num > range.max) return false;
    
    return true;
  };

  const handleNumberChange = (column, index, value) => {
    if (value === '' || validateNumber(value, column)) {
      const newCardNumbers = { ...cardNumbers };
      newCardNumbers[column][index] = value;
      setCardNumbers(newCardNumbers);
      
      const errorKey = `${column}-${index}`;
      if (errors[errorKey]) {
        const newErrors = { ...errors };
        delete newErrors[errorKey];
        setErrors(newErrors);
      }
    }
  };

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

  const resetForm = () => {
    setCardName('');
    setCardNumbers({
      B: Array(5).fill(''),
      I: Array(5).fill(''),
      N: Array(5).fill(''),
      G: Array(5).fill(''),
      O: Array(5).fill('')
    });
    setIsDefault(false);
    setErrors({});
    setEditingCard(null);
  };

  // Load custom cards on component mount
  useEffect(() => {
    if (user?.telegram_id) {
      fetchUserCustomCards();
      fetchUserDefaultCard();
    }
  }, [user?.telegram_id]);

  return (
    <div className="konjo-selections-container">
      {/* Header */}
      <div className="konjo-header">
        <div className="konjo-header-left">
          <button className="custom-card-btn create-btn" onClick={() => navigate('/')}>
            <FontAwesomeIcon icon={faArrowLeft} />
            Back to Game
          </button>
        </div>

        <div className="konjo-header-right">
          <button 
            className="custom-card-btn manage-btn"
            onClick={() => setShowCardManager(!showCardManager)}
          >
            <FontAwesomeIcon icon={faEye} />
            {showCardManager ? 'Hide' : 'Show'} My Cards
          </button>
        </div>
      </div>

      <div className="custom-board-content">
        {/* Card Manager */}
        {showCardManager && (
          <div className="card-manager-section">
            <h2>My Custom Cards</h2>
            {userCustomCards.length === 0 ? (
              <div className="no-cards">
                <p>No custom cards yet. Create your first one below!</p>
              </div>
            ) : (
              <div className="cards-grid">
                {userCustomCards.map((card) => (
                  <div key={card.id} className="card-item">
                    <div className="card-info">
                      <h3>{card.name}</h3>
                      {card.is_default && <span className="default-badge">Default</span>}
                    </div>
                    <div className="card-preview">
                      <div className="preview-header">
                        {['B', 'I', 'N', 'G', 'O'].map(letter => (
                          <div key={letter} className="preview-letter">{letter}</div>
                        ))}
                      </div>
                      <div className="preview-grid">
                        {['B', 'I', 'N', 'G', 'O'].map(column => (
                          <div key={column} className="preview-column">
                            {card.numbers[column].map((number, index) => (
                              <div key={index} className="preview-cell">{number}</div>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="card-actions">
                      <button 
                        className="edit-btn"
                        onClick={() => setEditingCard(card)}
                      >
                        <FontAwesomeIcon icon={faEdit} />
                        Edit
                      </button>
                      {!card.is_default && (
                        <button 
                          className="default-btn"
                          onClick={() => setDefaultCard(card.id)}
                        >
                          Set Default
                        </button>
                      )}
                      <button 
                        className="delete-btn"
                        onClick={() => deleteCustomCard(card.id)}
                      >
                        <FontAwesomeIcon icon={faTrash} />
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Card Editor */}
        <div className="card-editor-section">
          <h2>{editingCard ? 'Edit Card' : 'Create New Card'}</h2>
          
          <div className="editor-form">
          
         
            
            <div className="form-group">
              <button className="generate-btn" onClick={generateRandomCard}>
                Generate Random Card
              </button>
            </div>
            
            <div className="bingo-card-editor">
              <div className="bingo-header">
                {['B', 'I', 'N', 'G', 'O'].map(letter => (
                  <div key={letter} className="bingo-letter">{letter}</div>
                ))}
              </div>
              
              <div className="bingo-grid-editor">
                {['B', 'I', 'N', 'G', 'O'].map(column => (
                  <div key={column} className="bingo-column">
                    {cardNumbers[column].map((number, index) => (
                      <div key={index} className="bingo-cell-editor">
                        <input
                          type="number"
                          value={number}
                          onChange={(e) => handleNumberChange(column, index, e.target.value)}
                          className={`number-input ${errors[`${column}-${index}`] ? 'error' : ''}`}
                          placeholder={`${columnRanges[column].min}-${columnRanges[column].max}`}
                          min={columnRanges[column].min}
                          max={columnRanges[column].max}
                        />
                        {errors[`${column}-${index}`] && (
                          <div className="error-message">{errors[`${column}-${index}`]}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="form-actions">
              <button className="cancel-btn" onClick={resetForm}>
                Cancel
              </button>
              <button className="save-btn" onClick={saveCustomCard}>
                <FontAwesomeIcon icon={faSave} />
                {editingCard ? 'Update Card' : 'Save Card'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomBoard;
