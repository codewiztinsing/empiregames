#!/usr/bin/env python
"""
Script to reset all ReferralBonus records of type 'sponsor_change' (Sponsor Change Bonus 9 birr)

This script will:
1. Find all ReferralBonus records with bonus_type='sponsor_change'
2. Delete them from the database
3. Reset the sponsor_change_bonus_claimed field for all users
4. Provide a summary of actions taken

Usage:
    python reset_sponsor_change_bonuses.py

Make sure to run this from the Django project directory with the virtual environment activated.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, ReferralBonus
from django.db import transaction


def reset_sponsor_change_bonuses():
    """
    Reset all sponsor change bonuses and user flags
    """
    print("=" * 60)
    print("REFERRAL BONUS RESET SCRIPT")
    print("=" * 60)
    print()
    
    try:
        # Count existing sponsor change bonuses
        sponsor_change_bonuses = ReferralBonus.objects.filter(bonus_type='sponsor_change')
        total_bonuses = sponsor_change_bonuses.count()
        
        print(f"Found {total_bonuses} ReferralBonus records with type 'sponsor_change'")
        
        if total_bonuses == 0:
            print("No sponsor change bonuses found. Nothing to reset.")
            return
        
        # Show details of bonuses to be deleted
        print("\nBonuses to be deleted:")
        print("-" * 40)
        total_amount = 0
        for bonus in sponsor_change_bonuses:
            print(f"ID: {bonus.id} | User: {bonus.referrer.username} | Amount: {bonus.bonus_amount} ETB | Status: {bonus.status}")
            total_amount += bonus.bonus_amount
        
        print(f"\nTotal amount to be removed: {total_amount} ETB")
        
        # Count users with sponsor_change_bonus_claimed=True
        users_with_claimed_bonus = User.objects.filter(sponsor_change_bonus_claimed=True)
        users_count = users_with_claimed_bonus.count()
        
        print(f"\nFound {users_count} users with sponsor_change_bonus_claimed=True")
        
        # Confirm before proceeding
        print("\n" + "=" * 60)
        print("WARNING: This action cannot be undone!")
        print("=" * 60)
        
        confirm = input("\nDo you want to proceed? Type 'YES' to confirm: ")
        
        if confirm != 'YES':
            print("Operation cancelled.")
            return
        
        # Perform the reset operation
        with transaction.atomic():
            print("\nStarting reset operation...")
            
            # Delete all sponsor change bonuses
            deleted_count, deleted_details = sponsor_change_bonuses.delete()
            print(f"✓ Deleted {deleted_count} ReferralBonus records")
            
            # Reset sponsor_change_bonus_claimed for all users
            updated_users = User.objects.filter(sponsor_change_bonus_claimed=True).update(sponsor_change_bonus_claimed=False)
            print(f"✓ Reset sponsor_change_bonus_claimed flag for {updated_users} users")
            
            print("\n✓ Reset operation completed successfully!")
            
        # Final summary
        print("\n" + "=" * 60)
        print("RESET SUMMARY")
        print("=" * 60)
        print(f"• Deleted ReferralBonus records: {deleted_count}")
        print(f"• Reset user flags: {updated_users}")
        print(f"• Total amount removed: {total_amount} ETB")
        print(f"• Users affected: {users_count}")
        
        # Verify the reset
        remaining_bonuses = ReferralBonus.objects.filter(bonus_type='sponsor_change').count()
        remaining_users = User.objects.filter(sponsor_change_bonus_claimed=True).count()
        
        print(f"\nVerification:")
        print(f"• Remaining sponsor change bonuses: {remaining_bonuses}")
        print(f"• Users with claimed flag still set: {remaining_users}")
        
        if remaining_bonuses == 0 and remaining_users == 0:
            print("\n✓ Reset completed successfully - all sponsor change bonuses removed!")
        else:
            print("\n⚠ Warning: Some records may not have been reset properly.")
            
    except Exception as e:
        print(f"\n❌ Error during reset operation: {e}")
        print("Transaction rolled back. No changes were made.")
        raise


def show_current_status():
    """
    Show current status of sponsor change bonuses without making changes
    """
    print("=" * 60)
    print("CURRENT STATUS OF SPONSOR CHANGE BONUSES")
    print("=" * 60)
    
    # Count sponsor change bonuses
    sponsor_change_bonuses = ReferralBonus.objects.filter(bonus_type='sponsor_change')
    total_bonuses = sponsor_change_bonuses.count()
    
    print(f"Total sponsor change bonuses: {total_bonuses}")
    
    if total_bonuses > 0:
        print("\nBreakdown by status:")
        for status, _ in ReferralBonus.STATUS_CHOICES:
            count = sponsor_change_bonuses.filter(status=status).count()
            print(f"  {status}: {count}")
        
        print(f"\nTotal amount: {sponsor_change_bonuses.aggregate(total=models.Sum('bonus_amount'))['total'] or 0} ETB")
    
    # Count users with claimed flag
    users_with_claimed = User.objects.filter(sponsor_change_bonus_claimed=True).count()
    print(f"\nUsers with sponsor_change_bonus_claimed=True: {users_with_claimed}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse
    from django.db import models
    
    parser = argparse.ArgumentParser(description='Reset sponsor change bonuses')
    parser.add_argument('--status', action='store_true', help='Show current status without making changes')
    parser.add_argument('--reset', action='store_true', help='Reset all sponsor change bonuses')
    
    args = parser.parse_args()
    
    if args.status:
        show_current_status()
    elif args.reset:
        reset_sponsor_change_bonuses()
    else:
        print("ReferralBonus Reset Script")
        print("=" * 40)
        print("Usage:")
        print("  python reset_sponsor_change_bonuses.py --status  # Show current status")
        print("  python reset_sponsor_change_bonuses.py --reset   # Reset all sponsor change bonuses")
        print()
        print("This script will reset all ReferralBonus records of type 'sponsor_change'")
        print("and reset the sponsor_change_bonus_claimed flag for all users.")
