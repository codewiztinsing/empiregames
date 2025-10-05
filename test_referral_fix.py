#!/usr/bin/env python3
"""
Test script to verify referral processing fix
"""

import os
import sys
import django

# Add the app directory to Python path
sys.path.append('/var/www/akerbingo.com/empiregames/app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, ReferralBonus
from wallet.models import Wallet
from users.referral_services import ReferralService

def test_referral_processing():
    """Test the referral processing when a user wins"""
    print("=" * 60)
    print("TESTING REFERRAL PROCESSING FIX")
    print("=" * 60)
    
    # Find a user with a referrer
    user_with_referrer = User.objects.filter(referred_by__isnull=False).first()
    
    if not user_with_referrer:
        print("❌ No user with referrer found in database")
        print("   Please create a user with a referrer first")
        return False
    
    print(f"Testing with user: {user_with_referrer.username}")
    print(f"Telegram ID: {user_with_referrer.telegram_id}")
    print(f"Referred by: {user_with_referrer.referred_by.username}")
    
    # Get initial wallet balance
    wallet, created = Wallet.objects.get_or_create(user=user_with_referrer.referred_by)
    initial_balance = wallet.balance
    print(f"Initial referrer wallet balance: {initial_balance}")
    
    # Get initial total referral earnings
    initial_earnings = user_with_referrer.referred_by.total_referral_earnings
    print(f"Initial referrer total earnings: {initial_earnings}")
    
    # Count initial pending bonuses
    initial_pending_bonuses = ReferralBonus.objects.filter(
        referrer=user_with_referrer.referred_by, 
        status='pending'
    ).count()
    print(f"Initial pending bonuses: {initial_pending_bonuses}")
    
    # Test the referral processing
    test_win_amount = 1000.0
    test_game_id = "test_game_123"
    
    print(f"\nProcessing win bonus for {test_win_amount} birr...")
    
    try:
        result = ReferralService.process_win_bonus(
            user_with_referrer, 
            test_win_amount, 
            test_game_id
        )
        
        if result:
            print("✅ Referral processing completed successfully")
            
            # Check if bonuses were created and approved
            approved_bonuses = ReferralBonus.objects.filter(
                referrer=user_with_referrer.referred_by,
                status='approved',
                game_id=test_game_id
            )
            
            print(f"Created {approved_bonuses.count()} approved bonuses")
            
            for bonus in approved_bonuses:
                print(f"  - {bonus.bonus_type}: {bonus.bonus_amount} birr")
            
            # Check wallet balance
            wallet.refresh_from_db()
            new_balance = wallet.balance
            balance_increase = new_balance - initial_balance
            print(f"Wallet balance increased by: {balance_increase}")
            
            # Check total earnings
            user_with_referrer.referred_by.refresh_from_db()
            new_earnings = user_with_referrer.referred_by.total_referral_earnings
            earnings_increase = new_earnings - initial_earnings
            print(f"Total earnings increased by: {earnings_increase}")
            
            # Verify the amounts are correct
            expected_first_gen = test_win_amount * 0.04  # 4%
            expected_second_gen = test_win_amount * 0.01  # 1%
            
            if user_with_referrer.referred_by.referred_by:
                expected_total = expected_first_gen + expected_second_gen
            else:
                expected_total = expected_first_gen
            
            print(f"Expected total bonus: {expected_total}")
            print(f"Actual total bonus: {balance_increase}")
            
            if abs(balance_increase - expected_total) < 0.01:  # Allow for small floating point differences
                print("✅ Bonus amounts are correct!")
                return True
            else:
                print("❌ Bonus amounts don't match expected values")
                return False
                
        else:
            print("❌ Referral processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during referral processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST DATA")
    print("=" * 60)
    
    try:
        # Remove test bonuses
        test_bonuses = ReferralBonus.objects.filter(game_id="test_game_123")
        count = test_bonuses.count()
        test_bonuses.delete()
        print(f"Removed {count} test bonus records")
        
        return True
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    success = test_referral_processing()
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    print("TEST RESULT")
    print("=" * 60)
    if success:
        print("🎉 Referral processing fix is working correctly!")
    else:
        print("⚠️  Referral processing fix needs more work")
    
    sys.exit(0 if success else 1)

