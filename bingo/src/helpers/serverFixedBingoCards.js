// Fixed 5x5 Bingo Card Generator for Server
// This ensures consistent card generation on the server side

// Predefined card templates for consistent generation
const CARD_TEMPLATES = {
  // Template 1
  1: [
    [7, 23, 38, 52, 68],
    [12, 19, 35, 48, 61],
    [4, 16, '*', 45, 73],
    [9, 28, 42, 56, 70],
    [15, 31, 44, 59, 75]
  ],
  // Template 2
  2: [
    [3, 18, 33, 47, 62],
    [11, 25, 40, 54, 69],
    [6, 21, '*', 43, 66],
    [14, 29, 37, 51, 74],
    [8, 24, 39, 55, 71]
  ],
  // Template 3
  3: [
    [5, 20, 34, 49, 65],
    [13, 27, 41, 58, 72],
    [2, 17, '*', 46, 63],
    [10, 26, 36, 53, 67],
    [16, 30, 45, 57, 73]
  ],
  // Template 4
  4: [
    [1, 22, 37, 50, 64],
    [9, 24, 39, 52, 68],
    [7, 19, '*', 44, 61],
    [12, 28, 35, 48, 74],
    [15, 31, 42, 56, 70]
  ],
  // Template 5
  5: [
    [4, 21, 36, 51, 66],
    [11, 26, 38, 53, 69],
    [8, 18, '*', 43, 62],
    [14, 29, 37, 49, 73],
    [6, 23, 40, 55, 71]
  ]
};

// Generate a fixed card based on card number
function generateFixedCard(cardNumber) {
  // Use modulo to cycle through templates
  const templateIndex = ((cardNumber - 1) % 5) + 1;
  const template = CARD_TEMPLATES[templateIndex];
  
  if (!template) {
    // Fallback to template 1 if invalid
    return CARD_TEMPLATES[1];
  }
  
  // Return a deep copy of the template
  return template.map(row => [...row]);
}

// Generate multiple fixed cards
function generateMultipleFixedCards(count) {
  const cards = [];
  for (let i = 1; i <= count; i++) {
    cards.push(generateFixedCard(i));
  }
  return cards;
}

// Validate if a card follows the 5x5 structure
function validateCard(card) {
  if (!Array.isArray(card) || card.length !== 5) {
    return false;
  }
  
  for (let row of card) {
    if (!Array.isArray(row) || row.length !== 5) {
      return false;
    }
  }
  
  return true;
}

// Get card template by number
function getCardTemplate(cardNumber) {
  return generateFixedCard(cardNumber);
}

// Check if a number is valid for bingo (1-75)
function isValidBingoNumber(number) {
  return typeof number === 'number' && number >= 1 && number <= 75;
}

// Get all numbers from a card (excluding free space)
function getCardNumbers(card) {
  const numbers = [];
  for (let row of card) {
    for (let cell of row) {
      if (cell !== '*' && isValidBingoNumber(cell)) {
        numbers.push(cell);
      }
    }
  }
  return numbers;
}

// Check if a card has a specific number
function cardHasNumber(card, number) {
  for (let row of card) {
    for (let cell of row) {
      if (cell === number) {
        return true;
      }
    }
  }
  return false;
}

// Mark a number on a card
function markCardNumber(card, number) {
  const markedCard = card.map(row => [...row]);
  for (let row of markedCard) {
    for (let i = 0; i < row.length; i++) {
      if (row[i] === number) {
        row[i] = { number: number, marked: true };
      } else if (row[i] === '*') {
        row[i] = { number: '*', marked: true };
      } else if (typeof row[i] === 'object' && row[i].number === number) {
        row[i].marked = true;
      }
    }
  }
  return markedCard;
}

// Check for bingo patterns
function checkBingoPatterns(card) {
  const patterns = {
    row: false,
    column: false,
    diagonal: false,
    antiDiagonal: false,
    fourCorners: false,
    fourEdges: false
  };
  
  // Check rows
  for (let row of card) {
    if (row.every(cell => (typeof cell === 'object' && cell.marked) || cell === '*')) {
      patterns.row = true;
      break;
    }
  }
  
  // Check columns
  for (let col = 0; col < 5; col++) {
    if (card.every(row => {
      const cell = row[col];
      return (typeof cell === 'object' && cell.marked) || cell === '*';
    })) {
      patterns.column = true;
      break;
    }
  }
  
  // Check diagonal
  if (card.every((row, index) => {
    const cell = row[index];
    return (typeof cell === 'object' && cell.marked) || cell === '*';
  })) {
    patterns.diagonal = true;
  }
  
  // Check anti-diagonal
  if (card.every((row, index) => {
    const cell = row[4 - index];
    return (typeof cell === 'object' && cell.marked) || cell === '*';
  })) {
    patterns.antiDiagonal = true;
  }
  
  // Check four corners
  const corners = [
    card[0][0], card[0][4], card[4][0], card[4][4]
  ];
  if (corners.every(cell => (typeof cell === 'object' && cell.marked) || cell === '*')) {
    patterns.fourCorners = true;
  }
  
  // Check four edges (cross pattern)
  const edges = [
    card[0][2], card[2][0], card[2][4], card[4][2]
  ];
  if (edges.every(cell => (typeof cell === 'object' && cell.marked) || cell === '*')) {
    patterns.fourEdges = true;
  }
  
  return patterns;
}

// Check if card has any bingo
function hasBingo(card) {
  const patterns = checkBingoPatterns(card);
  return Object.values(patterns).some(pattern => pattern === true);
}

module.exports = {
  generateFixedCard,
  generateMultipleFixedCards,
  validateCard,
  getCardTemplate,
  isValidBingoNumber,
  getCardNumbers,
  cardHasNumber,
  markCardNumber,
  checkBingoPatterns,
  hasBingo
};
