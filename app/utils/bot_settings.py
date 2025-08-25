from decouple import config


def get_bot_seetings():
    BACK_URL = config('BACK_URL')   
    BOT_TOKEN = config('BOT_TOKEN')
    SERVER_URL = config('SERVER_URL')
    GAME_URL = config('GAME_URL')
    return {
        "bot_url":BACK_URL,
        "server_url":SERVER_URL,
        "bot_token":BOT_TOKEN,
        "GAME_URL":GAME_URL
    }

