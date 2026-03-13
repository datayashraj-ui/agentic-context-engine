#!/bin/bash
# NEXUS Oracle Cloud Setup Script
# Run as: bash scripts/setup-oracle.sh
# On a fresh Ubuntu 24.04 ARM64 instance

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[NEXUS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
header() { echo -e "\n${BLUE}========================================${NC}"; echo -e "${BLUE} $1${NC}"; echo -e "${BLUE}========================================${NC}"; }

# Verify ARM64
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
  warn "Not ARM64 (got: $ARCH). Continuing anyway but Docker images may not work correctly."
fi

header "NEXUS Setup — Oracle Cloud ARM64"
log "Starting at $(date)"
log "Architecture: $ARCH"

# ============================================================
# STEP 1: System packages
# ============================================================
header "Step 1: System Update"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
sudo apt-get install -y -qq \
  curl wget git vim htop \
  apt-transport-https \
  ca-certificates \
  gnupg \
  lsb-release \
  software-properties-common \
  build-essential \
  netfilter-persistent \
  iptables-persistent
log "System packages installed"

# ============================================================
# STEP 2: Docker
# ============================================================
header "Step 2: Docker & Docker Compose"
if command -v docker &>/dev/null; then
  log "Docker already installed: $(docker --version)"
else
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker "$USER"
  log "Docker installed: $(docker --version)"
fi

# Docker Compose plugin
if ! docker compose version &>/dev/null; then
  sudo apt-get install -y docker-compose-plugin
fi
log "Docker Compose: $(docker compose version)"

# ============================================================
# STEP 3: Coolify
# ============================================================
header "Step 3: Coolify (Deployment Platform)"
if [ -d "/data/coolify" ]; then
  log "Coolify already installed"
else
  log "Installing Coolify..."
  curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
  log "Coolify installed. Access at: http://$(curl -s ifconfig.me):8000"
fi

# ============================================================
# STEP 4: Clone repo
# ============================================================
header "Step 4: Clone NEXUS Repository"
NEXUS_HOME="/home/nexus"
sudo mkdir -p "$NEXUS_HOME"
sudo chown "$USER:$USER" "$NEXUS_HOME"

if [ -d "$NEXUS_HOME/nexus" ]; then
  log "Repo already cloned, pulling latest..."
  cd "$NEXUS_HOME/nexus" && git pull
else
  log "Enter your GitHub repo URL (e.g., https://github.com/yourusername/nexus.git):"
  read -r REPO_URL
  git clone "$REPO_URL" "$NEXUS_HOME/nexus"
  cd "$NEXUS_HOME/nexus"
fi
log "Repository ready at $NEXUS_HOME/nexus"

# ============================================================
# STEP 5: Environment setup
# ============================================================
header "Step 5: Environment Configuration"
cd "$NEXUS_HOME/nexus/infrastructure"

if [ ! -f ".env" ]; then
  cp .env.example .env
  log ".env file created from template"
  warn "You must edit .env with your actual values before continuing!"
  warn "Open another terminal and run: nano $NEXUS_HOME/nexus/infrastructure/.env"
  echo ""
  echo "Required values to fill in:"
  echo "  - TELEGRAM_BOT_TOKEN (from @BotFather on Telegram)"
  echo "  - FOUNDER_TELEGRAM_ID (your Telegram user ID)"
  echo "  - GOOGLE_API_KEY (from Google AI Studio)"
  echo "  - BASE_DOMAIN (your domain name)"
  echo "  - All DB passwords (generate random strings)"
  echo ""
  read -rp "Press Enter when .env is configured..."
else
  log ".env already exists, skipping"
fi

# Source env
set -a
source .env
set +a

# ============================================================
# STEP 6: Start Docker services
# ============================================================
header "Step 6: Starting Services"
cd "$NEXUS_HOME/nexus/infrastructure"
docker compose pull --quiet
docker compose up -d

log "Waiting for services to start (30s)..."
sleep 30

# Health check
RUNNING=$(docker compose ps --format json | grep -c '"State":"running"' || true)
log "$RUNNING services running"

# ============================================================
# STEP 7: Node.js + OpenClaw
# ============================================================
header "Step 7: Node.js & OpenClaw"
if ! command -v node &>/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
  log "Node.js installed: $(node --version)"
fi

log "Installing OpenClaw..."
sudo npm install -g openclaw@latest
log "OpenClaw installed: $(openclaw --version)"

# Copy config
cp "$NEXUS_HOME/nexus/infrastructure/openclaw-config.json5" "$HOME/.openclaw/config.json5" 2>/dev/null || {
  mkdir -p "$HOME/.openclaw"
  cp "$NEXUS_HOME/nexus/infrastructure/openclaw-config.json5" "$HOME/.openclaw/config.json5"
}

log "Starting OpenClaw onboarding..."
openclaw onboard --telegram-token "${TELEGRAM_BOT_TOKEN}" --non-interactive || {
  warn "OpenClaw onboard requires manual setup. Run: openclaw onboard"
}

# ============================================================
# STEP 8: Tailscale
# ============================================================
header "Step 8: Tailscale (Secure Remote Access)"
if ! command -v tailscale &>/dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
  log "Tailscale installed"
fi

if [ -n "${TAILSCALE_AUTH_KEY:-}" ]; then
  sudo tailscale up --authkey="$TAILSCALE_AUTH_KEY" --hostname=nexus-oracle
  log "Tailscale connected: $(tailscale status --json | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("Self",{}).get("TailscaleIPs",[["unknown"]])[0])')"
else
  warn "TAILSCALE_AUTH_KEY not set. Run manually: sudo tailscale up"
fi

# ============================================================
# STEP 9: ZeroClaw (Agent Daemon Runtime)
# ============================================================
header "Step 9: ZeroClaw (Agent Daemons)"
if ! command -v zeroclaw &>/dev/null; then
  log "Installing Rust toolchain for ZeroClaw..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  source "$HOME/.cargo/env"

  log "Cloning and building ZeroClaw..."
  cd /tmp
  git clone https://github.com/zeroclaw-labs/zeroclaw.git
  cd zeroclaw
  cargo build --release 2>/dev/null
  sudo cp target/release/zeroclaw /usr/local/bin/
  log "ZeroClaw installed: $(zeroclaw --version)"
fi

# Create systemd services for each agent daemon
AGENTS=("sales" "marketing" "support" "market-scout" "finance" "legal" "product-analyst" "watchdog")

for AGENT in "${AGENTS[@]}"; do
  SERVICE_FILE="/etc/systemd/system/nexus-${AGENT}.service"
  if [ ! -f "$SERVICE_FILE" ]; then
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=NEXUS ${AGENT} Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$NEXUS_HOME/nexus
ExecStart=/usr/local/bin/zeroclaw run agents/${AGENT}.md
Restart=always
RestartSec=10
Environment="GOOGLE_API_KEY=${GOOGLE_API_KEY}"
Environment="GROQ_API_KEY=${GROQ_API_KEY}"
EnvironmentFile=$NEXUS_HOME/nexus/infrastructure/.env

[Install]
WantedBy=multi-user.target
EOF
    log "Created systemd service: nexus-${AGENT}"
  fi
done

sudo systemctl daemon-reload
for AGENT in "${AGENTS[@]}"; do
  sudo systemctl enable "nexus-${AGENT}" --quiet
  sudo systemctl start "nexus-${AGENT}" || warn "Failed to start nexus-${AGENT}, check logs"
done
log "All agent daemons started"

# ============================================================
# STEP 10: Firewall configuration
# ============================================================
header "Step 10: Firewall"
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 22 -j ACCEPT 2>/dev/null || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT 2>/dev/null || true
sudo netfilter-persistent save 2>/dev/null || true
log "Firewall configured"

# ============================================================
# STEP 11: OpenClaw doctor
# ============================================================
header "Step 11: Health Check"
openclaw doctor || warn "Some checks failed. Review above output."

# ============================================================
# STEP 12: Send test Telegram message
# ============================================================
header "Step 12: Test Telegram"
TELEGRAM_MESSAGE="🦞 NEXUS is online. Your autonomous company is ready. Send 'status' to begin."

if curl -s -o /dev/null -w "%{http_code}" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${FOUNDER_TELEGRAM_ID}&text=${TELEGRAM_MESSAGE}" | grep -q "200"; then
  log "✅ Telegram test message sent successfully!"
else
  warn "Telegram message failed. Check TELEGRAM_BOT_TOKEN and FOUNDER_TELEGRAM_ID in .env"
fi

# ============================================================
# DONE
# ============================================================
header "NEXUS Setup Complete!"
echo ""
echo -e "${GREEN}Services running:${NC}"
echo "  OpenClaw gateway:  http://localhost:18789"
echo "  InsForge:          http://localhost:8001"
echo "  Coolify:           http://$(curl -s ifconfig.me):8000"
echo "  Langfuse:          http://localhost:3003"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Check your Telegram for the welcome message"
echo "  2. Reply 'status' to test the CEO agent"
echo "  3. Open Coolify at http://$(curl -s ifconfig.me):8000 and add your domain"
echo "  4. Point DNS to: $(curl -s ifconfig.me)"
echo ""
echo -e "${GREEN}Your company is running. Go build something.${NC}"
