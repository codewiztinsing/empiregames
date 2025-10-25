import React, { useState, useEffect } from 'react';
import './CustomCardManager.css';

const CustomCardManager = ({ isOpen, onClose, onSelectCard, onDeleteCard, userCustomCards = [] }) => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [cardToDelete, setCardToDelete] = useState(null);

  // Handle card selection
  const handleCardSelect = (card) => {
    setSelectedCard(card);
    onSelectCard(card);
    onClose();
  };

  // Handle delete confirmation
  const handleDeleteClick = (card) => {
    setCardToDelete(card);
    setShowDeleteConfirm(true);
  };

  // Confirm delete
  const confirmDelete = () => {
    if (cardToDelete) {
      onDeleteCard(cardToDelete.id);
      setShowDeleteConfirm(false);
      setCardToDelete(null);
    }
  };

  // Cancel delete
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setCardToDelete(null);
  };

  // Render bingo card preview
  const renderCardPreview = (card) => {
    return (
      <div className="card-preview">
        <div className="card-preview-header">
          {['B', 'I', 'N', 'G', 'O'].map(letter => (
            <div key={letter} className="preview-letter">{letter}</div>
          ))}
        </div>
        <div className="card-preview-grid">
          {['B', 'I', 'N', 'G', 'O'].map(column => (
            <div key={column} className="preview-column">
              {card.numbers[column].map((number, index) => (
                <div key={index} className="preview-cell">
                  {number}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="custom-card-manager-overlay">
      <div className="custom-card-manager">
        <div className="manager-header">
          <h2>My Custom Bingo Cards</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="manager-content">
          {userCustomCards.length === 0 ? (
            <div className="no-cards">
              <div className="no-cards-icon">🎯</div>
              <h3>No Custom Cards Yet</h3>
              <p>Create your first custom bingo card to get started!</p>
            </div>
          ) : (
            <div className="cards-grid">
              {userCustomCards.map((card) => (
                <div key={card.id} className="card-item">
                  <div className="card-info">
                    <h3 className="card-name">{card.name}</h3>
                    <div className="card-meta">
                      <span className="card-date">
                        Created: {new Date(card.createdAt).toLocaleDateString()}
                      </span>
                      {card.isDefault && (
                        <span className="default-badge">Default</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="card-preview-container">
                    {renderCardPreview(card)}
                  </div>
                  
                  <div className="card-actions">
                    <button 
                      className="select-btn"
                      onClick={() => handleCardSelect(card)}
                    >
                      Use This Card
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteClick(card)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="delete-confirm-overlay">
          <div className="delete-confirm-modal">
            <h3>Delete Custom Card</h3>
            <p>Are you sure you want to delete "{cardToDelete?.name}"?</p>
            <p className="warning-text">This action cannot be undone.</p>
            <div className="confirm-actions">
              <button className="cancel-btn" onClick={cancelDelete}>
                Cancel
              </button>
              <button className="confirm-delete-btn" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomCardManager;
