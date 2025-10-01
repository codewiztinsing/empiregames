#!/usr/bin/env python3
"""
Test script for referral logic in Aker Bingo Bot
Tests the referral flow: @testselambingobot ref_1464395537
"""

import requests
import json
import sys
import random
from datetime import datetime

# Configuration
BACK_URL = "http://localhost:8000"  # Update this to your actual backend URL
TEST_REFERRER_ID = 1464395537
TEST_USER_ID = random.randint(100000000, 999999999)  # Use a random test user ID

def test_referral_link_parsing():
    """Test parsing of referral link format: @testselambingobot ref_1464395537"""
    print("=" * 60)
    print("TEST 1: Referral Link Parsing")
    print("=" * 60)
    
    # Simulate the referral link format
    referral_link = "ref_1464395537"
    
    # Test the parsing logic from webbot.py line 1060-1061
    if referral_link.startswith("ref_"):
        referrer_id = int(referral_link.split("_")[1])
        print(f"✅ Referral link parsing successful")
        print(f"   Input: {referral_link}")
        print(f"   Parsed referrer_id: {referrer_id}")
        print(f"   Expected: {TEST_REFERRER_ID}")
        print(f"   Match: {referrer_id == TEST_REFERRER_ID}")
        return referrer_id
    else:
        print("❌ Referral link parsing failed")
        return None

def test_user_registration_with_referral():
    """Test user registration with referral data"""
    print("\n" + "=" * 60)
    print("TEST 2: User Registration with Referral")
    print("=" * 60)
    
    # Test user data
    user_data = {
        'telegram_id': str(TEST_USER_ID),
        'phone': f'+251911{random.randint(100000, 999999)}',  # Random test phone number
        'username': f'test_user_{TEST_USER_ID}',
        'password': '123456',
        'email': f'test_user_{TEST_USER_ID}@gmail.com',
        'first_name': 'Test',
        'last_name': 'User',
        'referred_by': str(TEST_REFERRER_ID)  # This is the key part - must be string
    }
    
    print(f"Registration data:")
    for key, value in user_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Make registration request
        response = requests.post(f"{BACK_URL}/api/v1/users/register", json=user_data)
        
        print(f"\nRegistration response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            print("✅ Registration successful")
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"   Error: {json.dumps(error_data, indent=2)}")
            print("❌ Registration failed")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_referral_relationship():
    """Test if referral relationship was created correctly"""
    print("\n" + "=" * 60)
    print("TEST 3: Verify Referral Relationship")
    print("=" * 60)
    
    try:
        # Get the registered user
        response = requests.get(f"{BACK_URL}/api/v1/users/{TEST_USER_ID}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"User data retrieved:")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Telegram ID: {user_data.get('telegram_id')}")
            print(f"   Referred by: {user_data.get('referred_by')}")
            
            # Check if referred_by matches our test referrer
            referred_by = user_data.get('referred_by')
            if referred_by == TEST_REFERRER_ID:
                print("✅ Referral relationship created correctly")
                return True
            else:
                print(f"❌ Referral relationship incorrect. Expected: {TEST_REFERRER_ID}, Got: {referred_by}")
                return False
        else:
            print(f"❌ Failed to retrieve user data. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking referral relationship: {e}")
        return False

def test_referrer_exists():
    """Test if the referrer user exists"""
    print("\n" + "=" * 60)
    print("TEST 4: Check if Referrer Exists")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACK_URL}/api/v1/users/{TEST_REFERRER_ID}")
        
        if response.status_code == 200:
            referrer_data = response.json()
            print(f"✅ Referrer exists:")
            print(f"   Username: {referrer_data.get('username')}")
            print(f"   Telegram ID: {referrer_data.get('telegram_id')}")
            return True
        else:
            print(f"❌ Referrer does not exist. Status: {response.status_code}")
            print("   This might cause registration to fail")
            return False
            
    except Exception as e:
        print(f"❌ Error checking referrer: {e}")
        return False

def cleanup_test_user():
    """Clean up test user after testing"""
    print("\n" + "=" * 60)
    print("CLEANUP: Remove Test User")
    print("=" * 60)
    
    try:
        # Note: You might need to implement a delete endpoint or do this manually
        print("⚠️  Manual cleanup required:")
        print(f"   Delete user with telegram_id: {TEST_USER_ID}")
        print(f"   Or implement a delete endpoint")
        return True
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return False

def main():
    """Run all referral tests"""
    print("AKER BINGO BOT - REFERRAL LOGIC TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print(f"Backend URL: {BACK_URL}")
    print(f"Test Referrer ID: {TEST_REFERRER_ID}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Referral link parsing
    referrer_id = test_referral_link_parsing()
    if referrer_id == TEST_REFERRER_ID:
        tests_passed += 1
    
    # Test 2: Check if referrer exists
    if test_referrer_exists():
        tests_passed += 1
    
    # Test 3: User registration with referral
    if test_user_registration_with_referral():
        tests_passed += 1
    
    # Test 4: Verify referral relationship
    if test_referral_relationship():
        tests_passed += 1
    
    # Cleanup
    cleanup_test_user()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Referral logic is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
