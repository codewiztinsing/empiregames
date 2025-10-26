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
  const [isSaving, setIsSaving] = useState(false);

  // Debug logging for cardName changes
  useEffect(() => {
    console.log('📝 [CardName] State changed:', { 
      cardName, 
      length: cardName?.length,
      trimmed: cardName?.trim(),
      trimmedLength: cardName?.trim()?.length
    });
  }, [cardName]);

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
    console.log('🎯 [SaveCard] Starting save card process...');
    console.log('🎯 [SaveCard] User data:', { 
      telegram_id: user?.telegram_id, 
      username: user?.username,
      hasUser: !!user 
    });
    
    if (!user?.telegram_id) {
      console.log('❌ [SaveCard] No user or telegram_id found, aborting');
      return;
    }
    
    console.log('🎯 [SaveCard] Card validation starting...');
    
    console.log('🎯 [SaveCard] Validating card data...');
    const isValid = validateCard();
    console.log('🎯 [SaveCard] Card validation result:', { isValid, errors });
    
    if (!isValid) {
      console.log('❌ [SaveCard] Card validation failed, showing error');
      setToast('Please fix all errors before saving');
      setIsToast(true);
      return;
    }
    
    console.log('🎯 [SaveCard] Setting saving state to true');
    setIsSaving(true);
    
    try {
      const cardData = {
        numbers: cardNumbers,
        is_default: isDefault
      };
      
      console.log('🎯 [SaveCard] Prepared card data:', {
        cardData,
        editingCard: editingCard ? { id: editingCard.id, name: editingCard.name } : null,
        isUpdate: !!editingCard
      });
      
      let result;
      if (editingCard) {
        console.log('🔄 [SaveCard] Updating existing card with ID:', editingCard.id);
        console.log('🔄 [SaveCard] Update payload:', {
          telegram_id: user.telegram_id,
          ...cardData
        });
        
        result = await customCardsAPI.updateCustomCard(editingCard.id, {
          telegram_id: user.telegram_id,
          ...cardData
        });
        
        console.log('✅ [SaveCard] Update API response:', result);
      } else {
        console.log('🆕 [SaveCard] Creating new card');
        console.log('🆕 [SaveCard] Create payload:', {
          telegram_id: user.telegram_id,
          ...cardData
        });
        
        result = await customCardsAPI.createCustomCard(user.telegram_id, cardData);
        
        console.log('✅ [SaveCard] Create API response:', result);
      }
      
      console.log('🎉 [SaveCard] Card saved successfully, showing success message');
      setToast(`✅ Custom card ${editingCard ? 'updated' : 'saved'} successfully!`);
      setIsToast(true);
      
      console.log('🔄 [SaveCard] Refreshing cards list and default card...');
      await fetchUserCustomCards();
      await fetchUserDefaultCard();
      
      console.log('🧹 [SaveCard] Resetting form and exiting edit mode');
      setEditingCard(null);
      resetForm();
      
      console.log('✅ [SaveCard] Save process completed successfully');
      
    } catch (error) {
      console.error('❌ [SaveCard] Error occurred during save:', error);
      console.error('❌ [SaveCard] Error details:', {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data,
        config: error.config,
        validationErrors: error.response?.data?.errors || error.response?.data?.error || 'No validation details'
      });
      
      // Extract detailed error message
      let errorMessage = 'Unknown error occurred';
      if (error.response?.data?.errors) {
        // Handle validation errors object
        const errors = error.response.data.errors;
        if (typeof errors === 'object') {
          errorMessage = Object.entries(errors)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
        } else {
          errorMessage = errors;
        }
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      console.log('❌ [SaveCard] Final error message:', errorMessage);
      
      setToast(`❌ Error saving custom card: ${errorMessage}`);
      setIsToast(true);
    } finally {
      console.log('🏁 [SaveCard] Setting saving state to false');
      setIsSaving(false);
    }
  };

  const deleteCustomCard = async (cardId) => {
    if (!user?.telegram_id) return;
    
    try {
      await customCardsAPI.deleteCustomCard(cardId);
      setToast(`✅ Custom card deleted successfully!`);
      setIsToast(true);
      
      // Refresh the cards list and default card
      await fetchUserCustomCards();
      await fetchUserDefaultCard();
      
    } catch (error) {
      console.error('Error deleting custom card:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error occurred';
      setToast(`❌ Error deleting custom card: ${errorMessage}`);
      setIsToast(true);
    }
  };

  const setDefaultCard = async (cardId) => {
    if (!user?.telegram_id) return;
    
    try {
      await customCardsAPI.setDefaultCard(cardId);
      setToast(`✅ Custom card set as default successfully!`);
      setIsToast(true);
      
      // Refresh the cards list and default card
      await fetchUserCustomCards();
      await fetchUserDefaultCard();
      
    } catch (error) {
      console.error('Error setting default card:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error occurred';
      setToast(`❌ Error setting default card: ${errorMessage}`);
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

  const generateRandomCard = async () => {
    if (!user?.telegram_id) return;
    
    try {
      // Try to get a random card from the API first
      const randomCardData = await customCardsAPI.generateRandomCard(user.telegram_id);
      
      if (randomCardData && randomCardData.numbers) {
        setCardNumbers(randomCardData.numbers);
        setErrors({});
        setToast('✅ Random card generated successfully!');
        setIsToast(true);
      } else {
        // Fallback to local generation
        generateRandomCardLocal();
      }
    } catch (error) {
      console.error('Error generating random card from API:', error);
      // Fallback to local generation
      generateRandomCardLocal();
    }
  };

  const generateRandomCardLocal = () => {
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
    console.log('🔍 [ValidateCard] Starting validation...');
    console.log('🔍 [ValidateCard] Card numbers to validate:', cardNumbers);
    
    const newErrors = {};
    const usedNumbers = new Set();
    
    Object.keys(columnRanges).forEach(column => {
      const range = columnRanges[column];
      console.log(`🔍 [ValidateCard] Validating column ${column} with range ${range.min}-${range.max}`);
      
      for (let i = 0; i < 5; i++) {
        const value = cardNumbers[column][i];
        const errorKey = `${column}-${i}`;
        
        console.log(`🔍 [ValidateCard] Validating ${column}[${i}] = "${value}"`);
        
        if (value === '') {
          newErrors[errorKey] = 'Number is required';
          console.log(`❌ [ValidateCard] ${errorKey}: Number is required`);
        } else {
          const num = parseInt(value);
          if (isNaN(num)) {
            newErrors[errorKey] = 'Invalid number';
            console.log(`❌ [ValidateCard] ${errorKey}: Invalid number "${value}"`);
          } else if (num < range.min || num > range.max) {
            newErrors[errorKey] = `Must be between ${range.min}-${range.max}`;
            console.log(`❌ [ValidateCard] ${errorKey}: Out of range ${num} (${range.min}-${range.max})`);
          } else if (usedNumbers.has(num)) {
            newErrors[errorKey] = 'Number already used';
            console.log(`❌ [ValidateCard] ${errorKey}: Number ${num} already used`);
          } else {
            usedNumbers.add(num);
            console.log(`✅ [ValidateCard] ${errorKey}: Valid number ${num}`);
          }
        }
      }
    });
    
    console.log('🔍 [ValidateCard] Validation complete:', {
      errors: newErrors,
      errorCount: Object.keys(newErrors).length,
      isValid: Object.keys(newErrors).length === 0,
      usedNumbers: Array.from(usedNumbers)
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const resetForm = () => {
    console.log('🧹 [ResetForm] Resetting form...');
    console.log('🧹 [ResetForm] Previous state:', {
      cardName,
      cardNumbers,
      isDefault,
      editingCard: editingCard ? { id: editingCard.id, name: editingCard.name } : null
    });
    
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
    
    console.log('🧹 [ResetForm] Form reset complete');
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
                      <h3>Card #{card.id}</h3>
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
              <label>
                <input
                  type="checkbox"
                  checked={isDefault}
                  onChange={(e) => {
                    console.log('🔘 [IsDefault] Checkbox changed:', { 
                      oldValue: isDefault, 
                      newValue: e.target.checked 
                    });
                    setIsDefault(e.target.checked);
                  }}
                />
                Set as default card
              </label>
            </div>
          
         
            
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
              <button className="save-btn" onClick={saveCustomCard} disabled={isSaving}>
                <FontAwesomeIcon icon={faSave} />
                {isSaving ? 'Saving...' : (editingCard ? 'Update Card' : 'Save Card')}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomBoard;
