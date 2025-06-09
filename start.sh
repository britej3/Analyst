#!/usr/bin/env bash
set -e
mkdir -p logs

# Start Ollama service
ollama serve > logs/ollama.log 2>&1 &

# Ensure Telegram token is provided
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "TELEGRAM_BOT_TOKEN not set" >&2
    exit 1
fi

# Start Telegram bot
python3 main_bot_py.py

