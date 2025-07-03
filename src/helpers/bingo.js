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

function checkBingo(markedCells,calledNumbers,currentCall){
    // Extract only numbers from calledNumbers array
    calledNumbers = calledNumbers.map(call => call.number);
    if (currentCall) {
        calledNumbers.push(currentCall.number);
    }
    let isBingo = false;
    const markedCard = turnMarkedCellsToCard(markedCells);
    const calledCard = turnCalledNumbersToCard(calledNumbers);
    // check if any row is complete
    for(let i = 0; i < 5; i++){
        if(markedCard[i].every(num => calledCard[i].includes(num))){
            isBingo = true;
        }
    }
    // check if any column is complete
    for(let i = 0; i < 5; i++){
        if(markedCard.every(row => row[i] === calledCard[i])){
            isBingo = true;
        }
    }

    // check if any diagonal is complete
    if(markedCard[0][0] === calledCard[0][0] && markedCard[1][1] === calledCard[1][1] && markedCard[2][2] === calledCard[2][2] && markedCard[3][3] === calledCard[3][3] && markedCard[4][4] === calledCard[4][4]){
        isBingo = true;
    }

    // check if any diagonal is complete
    if(markedCard[0][4] === calledCard[0][4] && markedCard[1][3] === calledCard[1][3] && markedCard[2][2] === calledCard[2][2] && markedCard[3][1] === calledCard[3][1] && markedCard[4][0] === calledCard[4][0]){
        isBingo = true;
    }

    // check if four corners are complete
    if(markedCard[0][0] === calledCard[0][0] && markedCard[0][4] === calledCard[0][4] && markedCard[4][0] === calledCard[4][0] && markedCard[4][4] === calledCard[4][4]){
        isBingo = true;
    }
    
    return isBingo;
}

module.exports = { checkBingo };