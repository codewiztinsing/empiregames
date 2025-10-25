#!/usr/bin/env python3
"""
Startup script for the standalone Agent Bot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'python-telegram-bot',
        'python-decouple'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_config():
    """Check if configuration file exists"""
    config_file = Path(__file__).parent / "config.env"
    if not config_file.exists():
        print("❌ Configuration file not found!")
        print("Please copy config.env.example to config.env and fill in your bot token.")
        return False
    
    return True

def load_env():
    """Load environment variables from config file"""
    try:
        from decouple import config
        config_file = Path(__file__).parent / "config.env"
        os.environ.setdefault('DECOUPLE_CONFIG_FILE', str(config_file))
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def main():
    """Main startup function"""
    print("🤖 Starting Agent Bot...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Load environment
    if not load_env():
        sys.exit(1)
    
    # Check bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'your_bot_token_here':
        print("❌ Please set your TELEGRAM_BOT_TOKEN in config.env")
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("🚀 Starting bot...")
    
    # Import and run the bot
    try:
        from standalone_agent_bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
