from ninja import Schema

class BetSchema(Schema):
    players: list[int]
    game_id: int
    bet_amount: float


class GameSchema(Schema):
    game_id: int
    bet_amount: int


class WinGameSchema(Schema):
    player: int
    game_id: int
    win_amount: float


class NextGameSchema(Schema):
    bet_amount: int


    
