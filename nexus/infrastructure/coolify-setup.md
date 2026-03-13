# Coolify Setup Guide

Coolify is the self-hosted deployment platform. It handles:
- Reverse proxy (Traefik) with automatic SSL via Let's Encrypt
- Deploy-on-push from GitHub
- Environment variable management
- Domain routing for all services

## Installation

Coolify is installed separately (not in Docker Compose) because it manages Docker itself.

```bash
# Install Coolify (run as root on Oracle Cloud instance)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

After installation, access at: `http://YOUR_SERVER_IP:8000`

## Initial Setup

1. Open `http://YOUR_SERVER_IP:8000` in browser
2. Create admin account
3. Go to Settings → SSH → Add your server (localhost)
4. Go to Sources → Add GitHub source (connect your GitHub account)

## Configure Domains

Go to Settings → Proxy → Add domains for each service:

| Service | Internal URL | External Domain |
|---------|-------------|-----------------|
| Voice Lab App | http://localhost:3004 | voicelab.yourdomain.com |
| Support (Chatwoot) | http://localhost:3000 | support.yourdomain.com |
| Analytics (PostHog) | http://localhost:8010 | analytics.yourdomain.com |
| CRM (Twenty) | http://localhost:3002 | crm.yourdomain.com |
| Automation (n8n) | http://localhost:5678 | automation.yourdomain.com |
| Errors (GlitchTip) | http://localhost:8080 | errors.yourdomain.com |
| Traces (Langfuse) | http://localhost:3003 | traces.yourdomain.com |
| Coolify Dashboard | — | deploy.yourdomain.com |

## Deploy Voice Lab (Product #1)

1. In Coolify → New Application
2. Source: GitHub → select `nexus` repo
3. Branch: `main`
4. Build pack: Docker Compose
5. Docker Compose file: `products/elevenlabs-clone/docker-compose.yml`
6. Add environment variables from `.env`
7. Set domain: `voicelab.yourdomain.com`
8. Enable "Deploy on push"
9. Copy webhook URL → paste in GitHub Actions workflow

## Automatic Deploy on PR Merge

GitHub Actions sends webhook to Coolify on merge to main:

```yaml
# .github/workflows/nexus-ci.yml
- name: Deploy to Coolify
  if: success()
  run: |
    curl -X POST "${{ secrets.COOLIFY_WEBHOOK_URL }}" \
      -H "Authorization: Bearer ${{ secrets.COOLIFY_TOKEN }}"
```

## SSL Certificates

Coolify uses Let's Encrypt automatically. Requirements:
- Domain DNS must point to Oracle Cloud IP
- Port 80 and 443 must be open in Oracle Cloud security list
- No manual certificate management needed

## Monitoring Deployments

- Coolify dashboard shows all deployments with logs
- Failed deployments trigger GlitchTip alert (via webhook)
- CEO agent gets notified via OpenClaw on deployment events
