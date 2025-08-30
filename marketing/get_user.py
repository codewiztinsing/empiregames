import asyncio
from dotenv import dotenv_values

config = dotenv_values(".env")

API_ID = config['API_ID']
API_HASH = config['API_HASH']
PHONE_NUMBER = config['PHONE_NUMBER']
import csv
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# https://t.me/addis_bingo
async def scrape_telegram_channel_users(channel_username, output_file=None):
    """
    Scrape all users from a Telegram channel
    
    Args:
        channel_username: The username or invite link of the channel
        output_file: Optional CSV file to save the results
    """
    
    client = TelegramClient('session', API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE_NUMBER)
        print(f"Connected to Telegram as {PHONE_NUMBER}")
        
        # Get the channel entity
        channel = await client.get_entity(channel_username)
        print(f"Scraping users from: {channel.title}")
        
        all_participants = []
        offset = 0
        limit = 100
        
        while True:
            try:
                participants = await client(GetParticipantsRequest(
                    channel,
                    ChannelParticipantsSearch(''),
                    offset,
                    limit,
                    hash=0
                ))
                
                if not participants.users:
                    break
                
                for user in participants.users:
                    user_data = {
                        'user_id': user.id,
                        'username': user.username if user.username else 'No username',
                        'phone': user.phone if user.phone else 'No phone',
                        'first_name': user.first_name if user.first_name else 'No first name',
                        'last_name': user.last_name if user.last_name else 'No last name',
                        'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip()
                    }
                    all_participants.append(user_data)
                
                offset += len(participants.users)
                print(f"Scraped {len(all_participants)} users so far...")
                
                # Add delay to avoid hitting rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error getting participants: {e}")
                break
        
        print(f"Total users scraped: {len(all_participants)}")
        
        # Save to CSV if output file is specified
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['user_id', 'username', 'phone', 'first_name', 'last_name', 'full_name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for user in all_participants:
                    writer.writerow(user)
            
            print(f"Results saved to {output_file}")
        
        return all_participants
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        await client.disconnect()

async def scrape_multiple_channels(channels, base_filename="telegram_users"):
    """
    Scrape users from multiple channels
    
    Args:
        channels: List of channel usernames/links
        base_filename: Base name for output files
    """
    
    for i, channel in enumerate(channels):
        print(f"\n--- Scraping channel {i+1}/{len(channels)}: {channel} ---")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{base_filename}_{i+1}_{timestamp}.csv"
        
        users = await scrape_telegram_channel_users(channel, output_file)
        
        # Add delay between channels
        if i < len(channels) - 1:
            print("Waiting 10 seconds before next channel...")
            await asyncio.sleep(10)

# Example usage
async def main():
    # Single channel scraping
    channel_username = "addis_bingo"  # Replace with actual channel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"telegram_channel_members_{timestamp}.csv"
    
    users = await scrape_telegram_channel_users(channel_username, output_file)

if __name__ == "__main__":
    asyncio.run(main())