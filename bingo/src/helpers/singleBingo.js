function checkSingleCardBingo(markedCard) {
    // Check rows for bingo
    for (let row = 0; row < 5; row++) {
        if (markedCard[row].every(cell => cell.marked)) {
            return true;
        }
    }

    // Check columns for bingo
    for (let col = 0; col < 5; col++) {
        if (markedCard.every(row => row[col].marked)) {
            return true;
        }
    }

    // Check diagonal from top-left to bottom-right
    if (markedCard[0][0].marked && 
        markedCard[1][1].marked && 
        markedCard[2][2].marked && 
        markedCard[3][3].marked && 
        markedCard[4][4].marked) {
        return true;
    }

    // Check diagonal from top-right to bottom-left
    if (markedCard[0][4].marked && 
        markedCard[1][3].marked && 
        markedCard[2][2].marked && 
        markedCard[3][1].marked && 
        markedCard[4][0].marked) {
        return true;
    }

    // Check four corners
    if (markedCard[0][0].marked && 
        markedCard[0][4].marked &&
        markedCard[4][0].marked && 
        markedCard[4][4].marked) {
        return true;
    }

    return false;
}

module.exports = { checkSingleCardBingo };
