# NEXUS Windows Setup Script
# Run in PowerShell as Administrator
# Sets up the CTO Agent development environment on Windows + WSL2

param(
    [switch]$SkipWSL,
    [switch]$SkipClaudeCode,
    [switch]$SkipMCP
)

$ErrorActionPreference = "Stop"

function Write-Header { param($text) Write-Host "`n========================================" -ForegroundColor Blue; Write-Host " $text" -ForegroundColor Blue; Write-Host "========================================`n" -ForegroundColor Blue }
function Write-Log { param($text) Write-Host "[NEXUS] $text" -ForegroundColor Green }
function Write-Warn { param($text) Write-Host "[WARN]  $text" -ForegroundColor Yellow }

Write-Header "NEXUS Windows CTO Environment Setup"
Write-Log "Setting up CTO agent environment on Windows + WSL2"

# ============================================================
# STEP 1: Check / Install WSL2
# ============================================================
Write-Header "Step 1: WSL2"
if (-not $SkipWSL) {
    $wslStatus = wsl --status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Installing WSL2..."
        wsl --install -d Ubuntu-24.04
        Write-Log "WSL2 installed. Restart your PC, then re-run this script with -SkipWSL"
        Read-Host "Press Enter to restart now (or Ctrl+C to restart manually later)"
        Restart-Computer
    } else {
        Write-Log "WSL2 already installed"
    }
} else {
    Write-Log "Skipping WSL2 install (-SkipWSL flag)"
}

# ============================================================
# STEP 2: Install tools in WSL2
# ============================================================
Write-Header "Step 2: Development Tools (via WSL2)"

$wslSetupScript = @'
#!/bin/bash
set -euo pipefail

echo "[WSL] Updating packages..."
sudo apt-get update -qq && sudo apt-get upgrade -y -qq

echo "[WSL] Installing base tools..."
sudo apt-get install -y -qq \
    curl wget git vim htop build-essential \
    python3.12 python3.12-pip python3.12-venv \
    python3-pip pipx

echo "[WSL] Installing Node.js 22..."
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
echo "Node: $(node --version), npm: $(npm --version)"

echo "[WSL] Installing Python tools..."
pip3 install --user uv pipx
pipx ensurepath

echo "[WSL] Installing SpecKit..."
pip3 install specify-cli
specify --version

echo "[WSL] Installing Beads CLI..."
npm install -g beads-cli@latest

echo "[WSL] Installing Lazygit..."
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_arm64.tar.gz"
tar xf lazygit.tar.gz lazygit
sudo install lazygit /usr/local/bin
rm lazygit.tar.gz lazygit

echo "[WSL] Dev tools installed!"
'@

Write-Log "Running setup inside WSL2..."
$wslSetupScript | wsl bash

# ============================================================
# STEP 3: Claude Code
# ============================================================
Write-Header "Step 3: Claude Code (CTO Agent)"
if (-not $SkipClaudeCode) {
    Write-Log "Installing Claude Code in WSL2..."
    wsl bash -c "curl -fsSL https://claude.ai/install.sh | bash"
    Write-Log "Claude Code installed"
    Write-Warn "You'll need to authenticate with: claude auth login"
} else {
    Write-Log "Skipping Claude Code install"
}

# ============================================================
# STEP 4: Gemini CLI (free research model)
# ============================================================
Write-Header "Step 4: Gemini CLI"
wsl bash -c "npm install -g @google/gemini-cli@latest && echo 'Gemini CLI: '$(gemini --version)"

# ============================================================
# STEP 5: Continue CLI (AI code review)
# ============================================================
Write-Header "Step 5: Continue CLI"
wsl bash -c "npm install -g @continuedev/continue-cli@latest && echo 'Continue CLI installed'"

# ============================================================
# STEP 6: Jules Tools (free maintenance automation)
# ============================================================
Write-Header "Step 6: Jules Tools"
wsl bash -c "npm install -g @google/jules-cli@latest 2>/dev/null || echo 'Jules CLI: install from https://jules.google.com'"

# ============================================================
# STEP 7: MCP Servers
# ============================================================
Write-Header "Step 7: MCP Servers"
if (-not $SkipMCP) {
    $mcpServers = @(
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-sequential-thinking",
        "@context7/mcp-server",
        "@playwright/mcp@latest",
        "cognee-mcp",
        "insforge-mcp",
        "docker-mcp",
        "@stripe/mcp",
        "@composio/mcp"
    )

    foreach ($server in $mcpServers) {
        Write-Log "Installing MCP: $server"
        wsl bash -c "npm install -g '$server' 2>/dev/null || npx --yes '$server' --version 2>/dev/null || echo 'Note: $server may require manual config'"
    }

    Write-Log "Configuring MCP servers in Claude Code..."
    $mcpConfig = @'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/user"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp"],
      "env": {
        "STRIPE_SECRET_KEY": "YOUR_STRIPE_KEY"
      }
    },
    "composio": {
      "command": "npx",
      "args": ["-y", "@composio/mcp"]
    }
  }
}
'@
    wsl bash -c "mkdir -p ~/.config/claude && echo '$mcpConfig' > ~/.config/claude/mcp-servers.json"
    Write-Log "MCP servers configured"
} else {
    Write-Log "Skipping MCP install (-SkipMCP flag)"
}

# ============================================================
# STEP 8: Claude Code Plugin Marketplaces
# ============================================================
Write-Header "Step 8: Claude Code Plugins"

$pluginMarketplaces = @(
    "anthropics/skills",
    "jeremylongshore/claude-code-plugins",
    "kivilaid/plugin-marketplace",
    "obra/superpowers-marketplace"
)

foreach ($marketplace in $pluginMarketplaces) {
    Write-Log "Adding plugin marketplace: $marketplace"
    wsl bash -c "claude plugins add '$marketplace' 2>/dev/null || echo 'Marketplace $marketplace: add manually in Claude Code'"
}

$essentialPlugins = @(
    "skill-creator",
    "mcp-builder",
    "webapp-testing",
    "frontend-design",
    "feature-dev"
)

foreach ($plugin in $essentialPlugins) {
    Write-Log "Installing plugin: $plugin"
    wsl bash -c "claude plugins install '$plugin' 2>/dev/null || echo 'Plugin $plugin: install manually'"
}

# ============================================================
# STEP 9: SpecKit configuration
# ============================================================
Write-Header "Step 9: SpecKit"
wsl bash -c "specify init --ai claude 2>/dev/null || echo 'SpecKit: run manually with: specify init --ai claude'"

# ============================================================
# STEP 10: Docker Desktop
# ============================================================
Write-Header "Step 10: Docker Desktop"
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Warn "Docker Desktop not installed."
    Write-Warn "Download from: https://www.docker.com/products/docker-desktop/"
    Write-Warn "Enable WSL2 integration after install."
} else {
    Write-Log "Docker Desktop already installed: $(docker --version)"
}

# ============================================================
# DONE
# ============================================================
Write-Header "Setup Complete!"
Write-Host ""
Write-Host "CTO Agent Environment Ready:" -ForegroundColor Green
Write-Host "  Claude Code:   wsl claude" -ForegroundColor White
Write-Host "  Gemini CLI:    wsl gemini" -ForegroundColor White
Write-Host "  SpecKit:       wsl specify" -ForegroundColor White
Write-Host "  Lazygit:       wsl lazygit" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Run: wsl claude auth login" -ForegroundColor White
Write-Host "  2. Run: wsl claude (opens Claude Code in WSL2)" -ForegroundColor White
Write-Host "  3. Open the nexus repo in Claude Code" -ForegroundColor White
Write-Host "  4. Claude Code will read CLAUDE.md and start as CTO agent" -ForegroundColor White
Write-Host ""
Write-Host "You're ready to build." -ForegroundColor Green
