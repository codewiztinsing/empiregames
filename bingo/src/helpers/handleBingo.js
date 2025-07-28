const { markPlayerCard } = require('./bingo');
const { checkSingleCardBingo } = require('./singleBingo');
const { endGame } = require('./endGame');
const { gameWinWallet,gameLossWallet,updateLastGame,getGameSettings } = require('./api');

async function handleBingo(data,activeGames,io,gameIntervals,users){
    const game = activeGames.get(data.gameId);
    if (!game || game.status !== 'in-progress') return;

    const playerCards = game.players.get(data.playerId);
    if (!playerCards || !Array.isArray(playerCards)) return;
    const board = data.board
    const boardNumber = data.boardNumber
    console.log("boardNumber ",boardNumber)
    const markedSingleCard = markPlayerCard(board, game.calledNumbers)
    const isSingleBingo = checkSingleCardBingo(markedSingleCard)
    if(isSingleBingo){

      io.to(game.roomId).emit("winBingo", {
            isBingo: true,
            playerId: data.playerId,
            markedCells: markedSingleCard,
            winningCard: markedSingleCard,
            winner: data.playerId,
            calledNumbers: game.calledNumbers,
            playerCard: boardNumber,
            winner_Number: boardNumber,
            playerName: data.playerName,
            currentCall: game.currentCall,
            gameId: data.gameId,
            total_winAmount: game.total_winAmount,
            total_players: game.total_players,
            roomId: data.roomId
      })

      try {
        const total_players = game.selectedNumbers.length
        
        await gameWinWallet(data.playerId, game.roomId, game.total_winAmount);
      } catch (error) {
        console.error("Error processing win wallet:", error);
      }

      endGame(game,gameIntervals,users,io,activeGames);
    }

    else{
      io.to(game.roomId).emit("falseBingo", {
        isBingo: false,
        playerId: data.playerId,
        losser_board: boardNumber,
      })
    }
      

  
}

module.exports = { handleBingo };