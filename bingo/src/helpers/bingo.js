function turnMarkedCellsToCard(markedCells){
    const card = [];
    for(let i = 0; i < 5; i++) {
        const row = [];
        for(let j = 0; j < 5; j++) {
            const num = markedCells[j*5+i];
            if (num <= 15) {
                if (i === 0) row.push(num);
            } else if (num <= 30) {
                if (i === 1) row.push(num); 
            } else if (num <= 45) {
                if (i === 2) row.push(num);
            } else if (num <= 60) {
                if (i === 3) row.push(num);
            } else {
                if (i === 4) row.push(num);
            }
        }
        card.push(row);
    }
    return card;
}


function markPlayerCard(playerCard,calledNumbers){
   
    // Create a new marked card based on playerCard structure
    // Extract just the called numbers into an array
    const calledNumbersOnly = calledNumbers.map(num => num.number || num);
    const markedCard = playerCard.map(row => {
     
        return row.map(cell => {
            return {
                number: cell,
                marked: calledNumbersOnly.includes(cell)
            };
        });
    });
    
    console.log("markedCard in markPlayerCard",markedCard)
    return markedCard;
}

function turnCalledNumbersToCard(calledNumbers){
    const card = [];
    for(let i = 0; i < 5; i++) {
        const row = [];
        for(let j = 0; j < 5; j++) {
            const num = calledNumbers[j*5+i];
            if (num <= 15) {
                if (i === 0) row.push(num);
            } else if (num <= 30) {
                if (i === 1) row.push(num); 
            } else if (num <= 45) {
                if (i === 2) row.push(num);
            } else if (num <= 60) {
                if (i === 3) row.push(num);
            } else {
                if (i === 4) row.push(num);
            }
        }
        card.push(row);
    }
    return card;
}

function checkBingo(playerCard,calledNumbers){
    let isBingo = false;
    const markedCard = markPlayerCard(playerCard,calledNumbers);
    // Check rows for bingo
    for (let row = 0; row < 5; row++) {
        if (markedCard[row].every(cell => cell.marked)) {
            isBingo = true;
            return isBingo;
        }
    }

    // Check columns for bingo
    for (let col = 0; col < 5; col++) {
        if (markedCard.every(row => row[col].marked)) {
            isBingo = true;
            return isBingo;
        }
    }

    // Check diagonal from top-left to bottom-right
    if (markedCard[0][0].marked && 
        markedCard[1][1].marked && 
        markedCard[2][2].marked && 
        markedCard[3][3].marked && 
        markedCard[4][4].marked) {
        isBingo = true;
        return isBingo;
    }

    // Check diagonal from top-right to bottom-left
    if (markedCard[0][4].marked && 
        markedCard[1][3].marked && 
        markedCard[2][2].marked && 
        markedCard[3][1].marked && 
        markedCard[4][0].marked) {
        isBingo = true;
        return isBingo;
    }

    // Check four corners
    if (markedCard[0][0].marked && 
        markedCard[0][4].marked &&
        markedCard[4][0].marked && 
        markedCard[4][4].marked) {
        isBingo = true;
        return isBingo;
    }
   
    return isBingo;
}
    
   

module.exports = { checkBingo,markPlayerCard,turnCalledNumbersToCard,turnMarkedCellsToCard };