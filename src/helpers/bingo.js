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
    const marked = [];
    for(let i = 0; i < playerCard.length; i++) {
        const row = [];
        for(let j = 0; j < playerCard[i].length; j++) {
            if(calledNumbers.includes(playerCard[i][j])) {
                row.push(true);
            } else {
                row.push(false);
            }
        }
        marked.push(row);
    }

    // Check rows
    for(let i = 0; i < marked.length; i++) {
        const row = marked[i];
        if(row.every(cell => cell === true)) {
            isBingo = true;
            break;
        }
    }

    // Check columns
    for(let i = 0; i < marked.length; i++) {
        const column = marked.map(row => row[i]);
        if(column.every(cell => cell === true)) {
            isBingo = true;
            break;
        }
    }

    // Check diagonals
    const diagonal1 = marked.map((row, index) => row[index]);
    const diagonal2 = marked.map((row, index) => row[4 - index]);
    
    if(diagonal1.every(cell => cell === true) || diagonal2.every(cell => cell === true)) {
        isBingo = true;
    }
    
    return isBingo;
}
    
   

module.exports = { checkBingo,markPlayerCard,turnCalledNumbersToCard,turnMarkedCellsToCard };