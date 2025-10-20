import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, unquote
from django.conf import settings
import os


class TelegramWebAppValidator:
    """
    Validates Telegram WebApp init data
    """
    
    def __init__(self, bot_token=None):
        self.bot_token = bot_token or os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("Bot token is required for Telegram WebApp validation")
    
    def validate_init_data(self, init_data, max_age=86400):
        """
        Validate Telegram WebApp init data
        
        Args:
            init_data (str): The init data string from Telegram WebApp
            max_age (int): Maximum age of the data in seconds (default: 24 hours)
        
        Returns:
            dict: Parsed and validated init data, or None if validation fails
        """
        try:
            # Parse the init data
            parsed_data = dict(parse_qsl(init_data))
            
            # Extract hash
            received_hash = parsed_data.pop('hash', '')
            if not received_hash:
                return None
            
            # Check auth_date
            auth_date = parsed_data.get('auth_date')
            if not auth_date:
                return None
            
            # Check if data is not too old
            if int(time.time()) - int(auth_date) > max_age:
                return None
            
            # Create data check string
            data_check_string = '\n'.join([
                f"{key}={value}" 
                for key, value in sorted(parsed_data.items())
            ])
            
            # Create secret key
            secret_key = hmac.new(
                b"WebAppData", 
                self.bot_token.encode(), 
                hashlib.sha256
            ).digest()
            
            # Calculate hash
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare hashes
            if calculated_hash != received_hash:
                return None
            
            # Parse user data if present
            if 'user' in parsed_data:
                try:
                    parsed_data['user'] = json.loads(parsed_data['user'])
                except json.JSONDecodeError:
                    return None
            
            return parsed_data
            
        except Exception as e:
            print(f"Telegram WebApp validation error: {e}")
            return None
    
    def validate_user_data(self, user_data):
        """
        Validate user data structure
        
        Args:
            user_data (dict): User data from Telegram WebApp
        
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['id', 'first_name']
        
        for field in required_fields:
            if field not in user_data:
                return False
        
        # Validate user ID is numeric
        try:
            int(user_data['id'])
        except (ValueError, TypeError):
            return False
        
        return True


def validate_telegram_webapp_data(init_data, bot_token=None):
    """
    Convenience function to validate Telegram WebApp data
    
    Args:
        init_data (str): The init data string from Telegram WebApp
        bot_token (str): Bot token (optional, will use from settings if not provided)
    
    Returns:
        dict: Validated data or None if validation fails
    """
    try:
        validator = TelegramWebAppValidator(bot_token)
        return validator.validate_init_data(init_data)
    except Exception as e:
        print(f"Telegram WebApp validation failed: {e}")
        return None
