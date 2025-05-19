#!/bin/bash

# Activate Python virtual environment if you use one
# source venv/bin/activate

# Set PYTHONPATH to project root
export PYTHONPATH=$(pwd)

# Start the Flask API for ChromaDB (background)
echo "Starting Flask API (ChromaDB) on port 5001..."
nohup python3 src/api/chroma_api.py > flask_api.log 2>&1 &

# Start the Telegram bot agent (background)
echo "Starting Telegram bot agent..."
nohup python3 src/telegram_bot.py > telegram_bot.log 2>&1 &

# Start Cloudflare Named Tunnel (background)
echo "Starting Cloudflare Named Tunnel..."
nohup cloudflared tunnel --config ~/.cloudflared/config.yml run flask-treesurgeonhereford > cloudflared.log 2>&1 &

# (Optional) If you want to keep the quick tunnel for testing, comment out the line below
# nohup /opt/homebrew/bin/cloudflared tunnel --url http://localhost:5001 > cloudflared.log 2>&1 &

echo "All services started!"
echo "Check flask_api.log, telegram_bot.log, and cloudflared.log for logs." 