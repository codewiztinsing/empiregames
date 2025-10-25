#!/usr/bin/env python3
"""
Simplified standalone agent bot runner
"""

import os
import sys
import asyncio
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set the bot token
os.environ['TELEGRAM_BOT_TOKEN'] = '8154094611:AAFF2uibjzso6VHqGkgEtf17l1L7MnOZ1nY'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main_async():
    """Main async function"""
    try:
        from standalone_agent_bot import AgentBot
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            return
            
        logger.info("Creating bot...")
        bot = AgentBot(token)
        
        logger.info("Starting bot...")
        await bot.run()
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        logger.info("Starting Agent Bot...")
        
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(main_async())
        finally:
            loop.close()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
