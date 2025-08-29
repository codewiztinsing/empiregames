#!/bin/bash

echo "Setting up environment variables..."

# Check if .env already exists
if [ -f ".env" ]; then
    echo ".env file already exists. Do you want to overwrite it? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cp env.example .env
        echo ".env file updated from env.example"
    else
        echo "Setup cancelled. .env file not modified."
        exit 0
    fi
else
    cp env.example .env
    echo ".env file created from env.example"
fi

echo ""
echo "IMPORTANT: You need to edit the .env file and set your actual Telegram bot token!"
echo "Replace 'your_telegram_bot_token_here' with your real bot token from @BotFather"
echo ""
echo "To get a bot token:"
echo "1. Message @BotFather on Telegram"
echo "2. Use /newbot command"
echo "3. Follow the instructions"
echo "4. Copy the token and paste it in the .env file"
echo ""
echo "After setting the token, run: sudo docker compose up --build"
