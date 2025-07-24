from ninja import Schema

class PlayerSchema(Schema):
    playerId: int
    numberOfBoards: int

class BetSchema(Schema):
    players: list[PlayerSchema]
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




class GameSettingsSchema(Schema):
    game_speed: int
    count_down_time: int


class PlayerGamesCountSchema(Schema):
    player_games_count: int


class PlayerGamesCountSchema(Schema):
    player_games_count: int


class PlayerGamesCountSchema(Schema):
    player_games_count: int
