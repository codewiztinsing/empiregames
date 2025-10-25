#!/bin/bash

# Quick Start Script for Empire Support Bot
# This script provides a simple way to start the bot for testing

set -e

# Configuration
BOT_DIR="/home/tinsae/Desktop/projects/empiregames/app/bot"
PYTHON_ENV="/home/tinsae/Desktop/projects/empiregames/app/venv"

echo "🚀 Starting Empire Support Bot..."

# Check if virtual environment exists
if [ ! -d "$PYTHON_ENV" ]; then
    echo "❌ Virtual environment not found at $PYTHON_ENV"
    echo "Please create the virtual environment first:"
    echo "cd /home/tinsae/Desktop/projects/empiregames/app"
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Check if config file exists
if [ ! -f "$BOT_DIR/config.env" ]; then
    echo "❌ Config file not found. Creating from example..."
    if [ -f "$BOT_DIR/config.env.example" ]; then
        cp "$BOT_DIR/config.env.example" "$BOT_DIR/config.env"
        echo "✅ Config file created. Please edit $BOT_DIR/config.env with your bot token"
        exit 1
    else
        echo "❌ No config file found. Please create $BOT_DIR/config.env"
        exit 1
    fi
fi

# Activate virtual environment and start bot
cd "$BOT_DIR"
source "$PYTHON_ENV/bin/activate"

echo "✅ Starting bot..."
python support.py
