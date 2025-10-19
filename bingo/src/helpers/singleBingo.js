function checkSingleCardBingo(markedCard) {
    console.log('checkSingleCardBingo called with:', markedCard);
    
    // Check rows for bingo
    for (let row = 0; row < 5; row++) {
        if (markedCard[row].every(cell => cell.marked)) {
            console.log('Bingo found in row:', row);
            return true;
        }
    }

    // Check columns for bingo
    for (let col = 0; col < 5; col++) {
        if (markedCard.every(row => row[col].marked)) {
            console.log('Bingo found in column:', col);
            return true;
        }
    }

    // Check diagonal from top-left to bottom-right
    if (markedCard[0][0].marked && 
        markedCard[1][1].marked && 
        markedCard[2][2].marked && 
        markedCard[3][3].marked && 
        markedCard[4][4].marked) {
        console.log('Bingo found in diagonal (top-left to bottom-right)');
        return true;
    }

    // Check diagonal from top-right to bottom-left
    if (markedCard[0][4].marked && 
        markedCard[1][3].marked && 
        markedCard[2][2].marked && 
        markedCard[3][1].marked && 
        markedCard[4][0].marked) {
        console.log('Bingo found in diagonal (top-right to bottom-left)');
        return true;
    }

    // Check four corners
    if (markedCard[0][0].marked && 
        markedCard[0][4].marked &&
        markedCard[4][0].marked && 
        markedCard[4][4].marked) {
        console.log('Bingo found in four corners');
        return true;
    }

    console.log('No bingo found');
    return false;
}

module.exports = { checkSingleCardBingo };
