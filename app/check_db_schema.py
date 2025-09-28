#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def check_user_table_schema():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users_user' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("Current users_user table schema:")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<25} {col[1]:<15} {col[2]:<10} {col[3] or 'None'}")
        print("-" * 80)
        
        # Check for specific fields that should exist
        expected_fields = [
            'referred_by_id', 'is_agent', 'sponsor_changed', 'total_referral_earnings',
            'total_games_played', 'games_played_today', 'games_played_this_week',
            'last_game_date', 'last_week_reset', 'created_at', 'updated_at'
        ]
        
        existing_columns = [col[0] for col in columns]
        missing_fields = [field for field in expected_fields if field not in existing_columns]
        
        if missing_fields:
            print(f"\nMissing fields: {missing_fields}")
        else:
            print("\nAll expected fields are present!")

if __name__ == "__main__":
    check_user_table_schema()
