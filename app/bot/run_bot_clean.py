#!/usr/bin/env python3
"""
Alternative runner for the standalone agent bot
This script runs the bot in a clean environment
"""

import os
import sys
import subprocess
import signal
import time

def signal_handler(sig, frame):
    print('\nShutting down bot...')
    sys.exit(0)

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set the bot token
    os.environ['TELEGRAM_BOT_TOKEN'] = '8320136714:AAHvPGC8EvP7qiJGiak5EKnt0-qrzmmb4IA'
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the bot script
    bot_script = os.path.join(script_dir, 'standalone_agent_bot.py')
    
    print("🤖 Starting Agent Bot...")
    print("Press Ctrl+C to stop the bot")
    
    try:
        # Run the bot script in a subprocess
        process = subprocess.Popen([sys.executable, bot_script])
        
        # Wait for the process to complete or be interrupted
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Bot stopped successfully")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        if 'process' in locals():
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
