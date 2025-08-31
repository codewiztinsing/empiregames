import csv
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import FloodWaitError, UsernameNotOccupiedError
from decouple import config

# Config
channel_name = "wowbingos"   # target group/channel username
API_ID = config("App api_id")
API_HASH = config("App api_hash")
phone = "+251940119495"

client = TelegramClient("marketing_client", API_ID, API_HASH)


def read_usernames_from_csv():
    """Read usernames from users_data.csv file"""
    usernames = []
    try:
        with open("users_data.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row.get("Username")
                if username and username.strip():
                    usernames.append(username.strip().lstrip("@"))  # remove @ if present
    except FileNotFoundError:
        print("❌ Error: users_data.csv file not found")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
    return usernames


async def add_users_to_channel():
    """Add users by username to a Telegram group/channel"""
    await client.start(phone=phone)

    try:
        channel = await client.get_entity(channel_name)
        print(f"✅ Found channel: {channel.title}")

        usernames = read_usernames_from_csv()
        print(f"📊 Loaded {len(usernames)} usernames from CSV")

        success_count, error_count = 0, 0

        for username in usernames:
            try:
                # Resolve user entity
                try:
                    user_entity = await client.get_entity(username)
                except UsernameNotOccupiedError:
                    print(f"⚠️ Username '{username}' does not exist")
                    error_count += 1
                    continue
                except Exception as resolve_error:
                    print(f"❌ Error resolving '{username}': {resolve_error}")
                    error_count += 1
                    continue

                # Try inviting user
                try:
                    await client(InviteToChannelRequest(
                        channel=channel,
                        users=[user_entity]
                    ))
                    print(f"✅ Added {username} to {channel_name}")
                    success_count += 1

                    # Delay to reduce spam detection
                    await asyncio.sleep(1)

                except FloodWaitError as f:
                    print(f"⏳ FloodWaitError: Sleeping for {f.seconds} seconds...")
                    await asyncio.sleep(f.seconds)
                except Exception as invite_error:
                    print(f"❌ Error adding {username}: {invite_error}")
                    error_count += 1

            except Exception as e:
                print(f"❌ Unexpected error with {username}: {e}")
                error_count += 1

        print(f"\n📊 Summary: {success_count} users added, {error_count} errors")

    except Exception as e:
        print(f"❌ Error accessing channel {channel_name}: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(add_users_to_channel())
