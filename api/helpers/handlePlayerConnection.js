const { createGame } = require('./handleCreateGame');

function handlePlayerConnection(socket,data,activeGames){
    console.log("data = ",data)
    socket.join(data.roomId)
    let game = activeGames.get(data.roomId) || createGame(data.roomId,activeGames);
    const inProgressGames = [...activeGames.values()].filter(g => g.status === 'in-progress');
    socket.to(data.roomId).emit("activeGames", { activeGames: inProgressGames });
    socket.emit("pickedNumbers", { roomId: game.roomId, numbers: game.selectedNumbers });
}


module.exports = {
    handlePlayerConnection
}