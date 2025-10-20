#!/usr/bin/env python3
"""
Test script for Telegram WebApp authentication
Run this script to test the authentication endpoints
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Add the Django project to the Python path
sys.path.append('/home/tinsae/Desktop/projects/empiregames/app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from users.telegram_validator import TelegramWebAppValidator

def test_telegram_validator():
    """Test the Telegram WebApp validator"""
    print("Testing Telegram WebApp Validator...")
    
    # Mock bot token (replace with your actual bot token)
    bot_token = "YOUR_BOT_TOKEN_HERE"
    
    try:
        validator = TelegramWebAppValidator(bot_token)
        print("✅ TelegramWebAppValidator initialized successfully")
        
        # Test with mock data (this would normally come from Telegram)
        mock_init_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%2C%22last_name%22%3A%22User%22%2C%22username%22%3A%22testuser%22%7D&auth_date=1640995200&hash=test_hash"
        
        # Note: This will fail with mock data, but tests the structure
        result = validator.validate_init_data(mock_init_data)
        if result is None:
            print("✅ Validator correctly rejected invalid mock data")
        else:
            print("⚠️ Validator accepted mock data (unexpected)")
            
    except Exception as e:
        print(f"❌ TelegramWebAppValidator test failed: {e}")

def test_user_model():
    """Test the User model"""
    print("\nTesting User Model...")
    
    try:
        # Check if we can create a test user
        test_telegram_id = "123456789"
        
        # Clean up any existing test user
        User.objects.filter(telegram_id=test_telegram_id).delete()
        
        # Create a test user
        user = User.objects.create(
            username="testuser",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            telegram_id=test_telegram_id,
            password="testpassword123"
        )
        
        print(f"✅ Test user created: {user.username} (ID: {user.id})")
        
        # Test retrieval
        retrieved_user = User.objects.get(telegram_id=test_telegram_id)
        print(f"✅ User retrieved successfully: {retrieved_user.username}")
        
        # Clean up
        user.delete()
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"❌ User model test failed: {e}")

def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    print("\nTesting API Endpoints...")
    
    base_url = "http://localhost:8000/api/v1/users"
    
    # Test endpoints that don't require authentication
    endpoints_to_test = [
        "/refresh-token",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {endpoint}: Server not running (expected in test environment)")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def test_environment():
    """Test environment setup"""
    print("\nTesting Environment Setup...")
    
    # Check Django settings
    from django.conf import settings
    print(f"✅ Django settings loaded: {settings.SETTINGS_MODULE}")
    
    # Check database connection
    from django.db import connection
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Check installed apps
    required_apps = ['users', 'game', 'wallet']
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✅ {app} app is installed")
        else:
            print(f"❌ {app} app is not installed")

def main():
    """Run all tests"""
    print("🚀 Starting Telegram WebApp Authentication Tests")
    print("=" * 50)
    
    test_environment()
    test_user_model()
    test_telegram_validator()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Set your BOT_TOKEN in the environment variables")
    print("2. Start the Django server: python manage.py runserver")
    print("3. Start the React development server: npm start")
    print("4. Test the authentication flow in Telegram WebApp")

if __name__ == "__main__":
    main()
