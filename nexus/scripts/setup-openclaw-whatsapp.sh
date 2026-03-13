#!/bin/bash
# Setup OpenClaw WhatsApp integration via WPPConnect
# Run after setup-oracle.sh

set -euo pipefail

log() { echo -e "\033[0;32m[NEXUS]\033[0m $1"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }

log "Setting up OpenClaw WhatsApp integration (WPPConnect)"

# Load env
if [ -f "../infrastructure/.env" ]; then
  source "../infrastructure/.env"
fi

# WPPConnect runs as a local server, OpenClaw connects to it
log "Starting WPPConnect server..."

# Install WPPConnect if not present
if ! command -v wppserver &>/dev/null; then
  npm install -g @wppconnect-team/wppserver@latest
fi

# Start WPPConnect server in background
wppserver --port 21465 &
WPPSERVER_PID=$!
log "WPPConnect server started (PID: $WPPSERVER_PID)"

sleep 5

# Generate QR code for WhatsApp link
log "Generating WhatsApp QR code..."
echo ""
echo "============================================"
echo "  SCAN THIS QR CODE WITH YOUR WHATSAPP"
echo "  Settings → Linked Devices → Link a device"
echo "============================================"
echo ""

# Request QR from WPPConnect
curl -s "http://localhost:21465/api/NEXUS/generate-token" \
  -H "Content-Type: application/json" \
  -d '{"secretKey": "NEXUS_WPP"}' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'status' in d:
    print('Status:', d['status'])
"

# WPPConnect will display QR in terminal
curl -s "http://localhost:21465/api/NEXUS/qr-code" \
  -H "Authorization: Bearer NEXUS_WPP"

echo ""
echo "============================================"
echo "After scanning:"
echo "  1. WhatsApp will show 'Linked device'"
echo "  2. Run: openclaw connect --whatsapp"
echo "  3. Test by messaging yourself from the bot"
echo "============================================"
echo ""

log "WhatsApp setup initiated. PID: $WPPSERVER_PID"
log "If QR didn't display, visit: http://localhost:21465"
warn "Keep this terminal open until scan is complete"

# Wait for connection
read -rp "Press Enter after scanning the QR code..."

# Test the connection
TEST_RESPONSE=$(curl -s "http://localhost:21465/api/NEXUS/check-connection-session" \
  -H "Authorization: Bearer NEXUS_WPP")

if echo "$TEST_RESPONSE" | grep -q '"status":"CONNECTED"'; then
  log "✅ WhatsApp connected successfully!"

  # Send test message to founder
  if [ -n "${FOUNDER_PHONE_NUMBER:-}" ]; then
    PHONE="${FOUNDER_PHONE_NUMBER//+/}@c.us"
    curl -s -X POST "http://localhost:21465/api/NEXUS/send-message" \
      -H "Authorization: Bearer NEXUS_WPP" \
      -H "Content-Type: application/json" \
      -d "{\"phone\": \"$PHONE\", \"message\": \"🟢 WhatsApp connected! NEXUS Support Agent is online.\"}"
    log "Test message sent to founder"
  fi
else
  warn "Connection status unclear. Check: http://localhost:21465"
fi

log "WhatsApp setup complete!"
