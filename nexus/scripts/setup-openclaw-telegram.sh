#!/bin/bash
# Setup OpenClaw Telegram integration
# Run after setup-oracle.sh

set -euo pipefail

log() { echo -e "\033[0;32m[NEXUS]\033[0m $1"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }

log "Setting up OpenClaw Telegram integration"

# Load env
if [ -f "../infrastructure/.env" ]; then
  source "../infrastructure/.env"
else
  warn "No .env found. Please provide values manually."
  read -rp "Telegram Bot Token (from @BotFather): " TELEGRAM_BOT_TOKEN
  read -rp "Your Telegram User ID: " FOUNDER_TELEGRAM_ID
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "Steps to get a Telegram Bot Token:"
  echo "1. Open Telegram"
  echo "2. Search for @BotFather"
  echo "3. Send: /newbot"
  echo "4. Follow prompts, copy the token"
  read -rp "Enter token: " TELEGRAM_BOT_TOKEN
fi

if [ -z "${FOUNDER_TELEGRAM_ID:-}" ]; then
  echo "Steps to get your Telegram User ID:"
  echo "1. Open Telegram"
  echo "2. Search for @userinfobot"
  echo "3. Send: /start"
  echo "4. Copy the ID number"
  read -rp "Enter your Telegram ID: " FOUNDER_TELEGRAM_ID
fi

# Test the bot token
RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
if echo "$RESPONSE" | grep -q '"ok":true'; then
  BOT_NAME=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['username'])")
  log "Bot verified: @$BOT_NAME"
else
  echo "Error: Invalid bot token. Response: $RESPONSE"
  exit 1
fi

# Update OpenClaw config
CONFIG="$HOME/.openclaw/config.json5"
if [ -f "$CONFIG" ]; then
  # Replace placeholder values
  sed -i "s/FOUNDER_TELEGRAM_ID/$FOUNDER_TELEGRAM_ID/g" "$CONFIG"
  log "OpenClaw config updated with Telegram settings"
fi

# Start the bot (send /start to it first)
log "Starting OpenClaw with Telegram..."
openclaw start --config "$CONFIG" &
OPENCLAW_PID=$!

sleep 3

# Send test message
curl -s -o /dev/null \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${FOUNDER_TELEGRAM_ID}&text=🤖 Telegram integration configured! Send 'status' to test."

log "Setup complete!"
log "Open Telegram and message @$BOT_NAME to test"
log "OpenClaw running with PID: $OPENCLAW_PID"
