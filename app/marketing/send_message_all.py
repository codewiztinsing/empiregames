import csv
import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, PeerFloodError, UserPrivacyRestrictedError
from decouple import config

# Config
API_ID = config("App api_id")
API_HASH = config("App api_hash")
phone = "+251940119495"

client = TelegramClient("marketing_client", API_ID, API_HASH)


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


async def send_message_to_all_users():
    """Send a message to all users from CSV file"""
    await client.start(phone=phone)

    # Message to send
    message = """
🎉 Welcome to WowBingos! 🎉
We're excited to have you join our community. Get ready for amazing bingo games and exciting prizes!
💰 Play daily games
🎁 Win incredible rewards  
👥 Join our growing community
Start playing now and let the fun begin!

@wowbingobotbotbot
Good luck! 🍀
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
            
            try:
                # Try to get user entity by telegram_id first, then by username
                user_entity = None
                
                try:
                    if telegram_id.isdigit():
                        user_entity = await client.get_entity(int(telegram_id))
                    else:
                        user_entity = await client.get_entity(telegram_id)
                except Exception:
                    if username:
                        try:
                            user_entity = await client.get_entity(username.lstrip('@'))
                        except Exception as e:
                            print(f"❌ Could not find user with telegram_id: {telegram_id}, username: {username}")
                            error_count += 1
                            continue

                if not user_entity:
                    print(f"❌ Could not resolve user: {telegram_id}")
                    error_count += 1
                    continue

                # Send message
                try:
                    await client.send_message(user_entity, message)
                    display_name = username if username else telegram_id
                    print(f"✅ Message sent to {display_name}")
                    success_count += 1

                    # Delay to avoid spam detection
                    await asyncio.sleep(2)

                except FloodWaitError as f:
                    print(f"⏳ FloodWaitError: Sleeping for {f.seconds} seconds...")
                    await asyncio.sleep(f.seconds)
                    # Retry sending message after flood wait
                    try:
                        await client.send_message(user_entity, message)
                        display_name = username if username else telegram_id
                        print(f"✅ Message sent to {display_name} (after flood wait)")
                        success_count += 1
                    except Exception as retry_error:
                        print(f"❌ Failed to send message after flood wait to {telegram_id}: {retry_error}")
                        error_count += 1

                except PeerFloodError:
                    print(f"❌ PeerFloodError: Too many requests. Stopping to avoid ban.")
                    break

                except UserPrivacyRestrictedError:
                    print(f"⚠️ User {telegram_id} has privacy restrictions")
                    error_count += 1

                except Exception as send_error:
                    print(f"❌ Error sending message to {telegram_id}: {send_error}")
                    error_count += 1

            except Exception as e:
                print(f"❌ Unexpected error with user {telegram_id}: {e}")
                error_count += 1

        print(f"\n📊 Summary: {success_count} messages sent, {error_count} errors")

    except Exception as e:
        print(f"❌ General error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(send_message_to_all_users())
