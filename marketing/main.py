import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import csv
from datetime import datetime

# Telegram API credentials (get these from https://my.telegram.org)
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
PHONE_NUMBER = 'your_phone_number'

# Group/Channel username or ID
GROUP_USERNAME = '@your_group_username'  # or group ID like -1001234567890

async def get_group_members():
    # Create the client
    client = TelegramClient('session', API_ID, API_HASH)
    
    try:
        # Start the client
        await client.start(phone=PHONE_NUMBER)
        
        # Get the group entity
        group = await client.get_entity(GROUP_USERNAME)
        
        print(f"Getting members from: {group.title}")
        
        # Get all participants
        all_participants = []
        offset = 0
        limit = 100
        
        while True:
            participants = await client(GetParticipantsRequest(
                group,
                ChannelParticipantsSearch(''),
                offset,
                limit,
                hash=0
            ))
            
            if not participants.users:
                break
                
            all_participants.extend(participants.users)
            offset += len(participants.users)
            
            print(f"Retrieved {len(all_participants)} members so far...")
        
        # Extract user data
        members_data = []
        for user in all_participants:
            username = user.username if user.username else "No username"
            phone = user.phone if user.phone else "No phone"
            first_name = user.first_name if user.first_name else "No first name"
            last_name = user.last_name if user.last_name else "No last name"
            user_id = user.id
            
            members_data.append({
                'user_id': user_id,
                'username': username,
                'phone': phone,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': f"{first_name} {last_name}".strip()
            })
        
        # Save to CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telegram_group_members_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['user_id', 'username', 'phone', 'first_name', 'last_name', 'full_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for member in members_data:
                writer.writerow(member)
        
        print(f"\nTotal members found: {len(members_data)}")
        print(f"Data saved to: {filename}")
        
        # Print summary
        with_phone = sum(1 for member in members_data if member['phone'] != "No phone")
        with_username = sum(1 for member in members_data if member['username'] != "No username")
        
        print(f"Members with phone numbers: {with_phone}")
        print(f"Members with usernames: {with_username}")
        
        return members_data
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

def main():
    """
    Main function to run the telegram scraper
    
    Before running:
    1. Install required packages: pip install telethon
    2. Get API credentials from https://my.telegram.org
    3. Update API_ID, API_HASH, PHONE_NUMBER, and GROUP_USERNAME
    4. Make sure you're a member of the target group
    """
    
    # Check if credentials are set
    if API_ID == 'your_api_id' or API_HASH == 'your_api_hash':
        print("Please update your API credentials in the script!")
        print("Get them from: https://my.telegram.org")
        return
    
    if GROUP_USERNAME == '@your_group_username':
        print("Please update the GROUP_USERNAME in the script!")
        return
    
    # Run the async function
    asyncio.run(get_group_members())

if __name__ == "__main__":
    main()
