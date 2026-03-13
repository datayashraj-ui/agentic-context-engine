#!/bin/bash
# NEXUS WSL2 Setup — run inside WSL2 Ubuntu terminal
# Installs the CTO agent dev environment

set -euo pipefail

log() { echo -e "\033[0;32m[NEXUS]\033[0m $1"; }
warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }

log "Setting up NEXUS CTO environment in WSL2"

# Update packages
sudo apt-get update -qq && sudo apt-get upgrade -y -qq
sudo apt-get install -y -qq curl wget git vim htop build-essential python3.12 python3-pip

# Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
log "Node.js: $(node --version)"

# Python UV
pip3 install --user uv
log "UV: $(uv --version)"

# Claude Code
if ! command -v claude &>/dev/null; then
  curl -fsSL https://claude.ai/install.sh | bash
  log "Claude Code installed"
else
  log "Claude Code: $(claude --version)"
fi

# Gemini CLI
npm install -g @google/gemini-cli@latest 2>/dev/null || warn "Gemini CLI install failed"

# SpecKit
pip3 install specify-cli
log "SpecKit: $(specify --version 2>/dev/null || echo 'installed')"

# Continue CLI
npm install -g @continuedev/continue-cli@latest 2>/dev/null || warn "Continue CLI install failed"

# Lazygit
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo /tmp/lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf /tmp/lazygit.tar.gz -C /tmp lazygit
sudo install /tmp/lazygit /usr/local/bin
rm /tmp/lazygit.tar.gz /tmp/lazygit
log "Lazygit: $(lazygit --version | head -1)"

log "WSL2 CTO environment ready!"
log "Run: claude auth login"
