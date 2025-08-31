import csv
import asyncio
import requests
from decouple import config

# Config
BOT_TOKEN = "8097767840:AAEI7JCS7O5YVlnoQVBBzdXweoEnEeJ7xsU"  # Your bot token from BotFather
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def read_users_from_csv():
    """Read user data from users_data.csv file"""
    users = []
    try:
        with open("users_data.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                telegram_id = row.get("Telegram ID")
                username = row.get("Username")
                if telegram_id and telegram_id.strip():
                    users.append({
                        'telegram_id': telegram_id.strip(),
                        'username': username.strip() if username else None
                    })
    except FileNotFoundError:
        print("❌ Error: users_data.csv file not found")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
    return users


async def send_message_to_user(telegram_id, message):
    """Send message to a specific user using Bot API"""
    url = f"{BOT_API_URL}/sendMessage"
    payload = {
        'chat_id': telegram_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response_data.get('ok'):
            return True, None
        else:
            error_description = response_data.get('description', 'Unknown error')
            return False, error_description
            
    except Exception as e:
        return False, str(e)


async def send_message_to_all_users():
    """Send a message to all users from CSV file using Bot API"""
    
    # Message to send
    message = """
    WOW✨✨BINGO✨እየተዝናኑ ያሸንፉ 🤙🤙
    🤳🤳 ከርስዎ የሚጠበቀው ቴሌግራም ላይ  @wowbingobotbotbot ብሎ search 🔍🔍 ማረግ እና ጨዋታውን መጫወት ብቻ
    💵ሲመዘገቡ የ 19 ብር ጉርሻ ያገኛሉ   
    💲ከ10 ብር ጀምሮ እንደምርጫዎ ሲጫወቱ እስከ 💵50,000 ብር ድረስ ማሸነፍ ይችላሉ

    ✍️ @wowbingobotbotbot
    ✍️ @wowbingobotbotbot
    ✍️ @wowbingobotbotbot

    https://t.me/wowbingos
    """.strip()

    try:
        users = read_users_from_csv()
        print(f"📊 Loaded {len(users)} users from CSV")

        if not users:
            print("❌ No users found to send messages to")
            return

        success_count, error_count = 0, 0

        for user_data in users:
            telegram_id = user_data['telegram_id']
            username = user_data['username']
            
            # Send message using Bot API
            success, error = await send_message_to_user(telegram_id, message)
            
            if success:
                display_name = username if username else telegram_id
                print(f"✅ Message sent to {display_name}")
                success_count += 1
            else:
                print(f"❌ Failed to send message to {telegram_id}: {error}")
                error_count += 1
            
            # Delay to avoid hitting rate limits
            await asyncio.sleep(0.1)  # 100ms delay between messages

        print(f"\n📊 Summary: {success_count} messages sent, {error_count} errors")

    except Exception as e:
        print(f"❌ General error: {e}")


if __name__ == "__main__":
    asyncio.run(send_message_to_all_users())
