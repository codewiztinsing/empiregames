#!/usr/bin/env python3
"""
Simple test script to run the standalone agent bot
"""

import os
import sys

# Set the bot token
os.environ['TELEGRAM_BOT_TOKEN'] = '8154094611:AAFF2uibjzso6VHqGkgEtf17l1L7MnOZ1nY'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the bot
if __name__ == "__main__":
    try:
        from standalone_agent_bot import main
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
