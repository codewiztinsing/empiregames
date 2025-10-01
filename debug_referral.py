#!/usr/bin/env python3
"""
Debug script to check referral data in the database
"""

import os
import sys
import django

# Add the app directory to Python path
sys.path.append('/home/tinsae/Desktop/projects/empiregames/app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def check_user_referral():
    """Check the referral relationship for the test user"""
    test_user_id = "535055476"
    
    try:
        # Get the test user
        user = User.objects.get(telegram_id=test_user_id)
        print(f"User found: {user.username}")
        print(f"Telegram ID: {user.telegram_id}")
        print(f"Referred by: {user.referred_by}")
        
        if user.referred_by:
            print(f"Referrer username: {user.referred_by.username}")
            print(f"Referrer telegram_id: {user.referred_by.telegram_id}")
        else:
            print("❌ No referrer found")
            
        # Check if the referrer exists
        referrer = User.objects.get(telegram_id="1464395537")
        print(f"\nReferrer exists: {referrer.username}")
        print(f"Referrer telegram_id: {referrer.telegram_id}")
        
    except User.DoesNotExist as e:
        print(f"❌ User not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_user_referral()
