from decouple import config


def get_bot_seetings():
    BACK_URL = config('BACK_URL')   
    BOT_TOKEN = config('BOT_TOKEN')
    return {
        "bot_url":BACK_URL,
        "bot_token":BOT_TOKEN,
    }

