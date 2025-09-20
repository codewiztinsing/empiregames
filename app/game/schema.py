from ninja import Schema
from .models import GameType

class PlayerSchema(Schema):
    playerId: int
    numberOfBoards: int




class BetSchema(Schema):
    players: list[PlayerSchema]
    game_id: int
    bet_amount: float

    # incoming data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("kwargs",kwargs)
        self.incoming_data = kwargs.get("incoming_data", {})
    

    


class GameSchema(Schema):
    game_id: int
    bet_amount: int
    playerId: int


class WinGameSchema(Schema):
    playerId: int
    game_id: int
    win_amount: float


class NextGameSchema(Schema):
    bet_amount: int




class GameSettingsSchema(Schema):
    game_speed: int
    count_down_time: int
    

class GameType(Schema):
    bet_amount: int
    commission: int

class GameTypeSchema(Schema):
    game_types: list[GameType]

class PlayerGameSchema(Schema):
    id: int
    username: str
    has_bingo: bool

class GameDetailsSchema(Schema):
    game_id: int
    bet_amount: int
    status: str
    winner: str = None
    players: list[PlayerGameSchema] = []
    total_players: int = 0
    created_at: str
    ended: bool
