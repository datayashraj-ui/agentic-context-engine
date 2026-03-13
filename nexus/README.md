# NEXUS — Autonomous AI Company

NEXUS is an autonomous AI company controlled entirely from Telegram and WhatsApp. The founder (Yash) runs this company from his Android phone. He messages his CEO agent, gives strategic direction, and the company builds, sells, and supports products autonomously.

**The CEO never sleeps. The engineers never quit. The company runs 24/7.**

---

## Your First Day

This is a step-by-step walkthrough of going from zero to a running autonomous company.

### Prerequisites
- Oracle Cloud account (free tier)
- Telegram account
- Android phone
- Your own domain name (~$10/year from Namecheap/Cloudflare)

---

### 1. Create Oracle Cloud Free Tier Account

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click **"Start for free"**
3. Enter your email → verify → complete signup
4. Choose region: pick one close to your customers (e.g., `ap-mumbai-1` for India)
5. Add a credit card (required for identity verification, NOT charged for free tier)

---

### 2. Create ARM Instance (Always Free)

1. Go to **Compute → Instances → Create Instance**
2. Name: `nexus-server`
3. Image: **Ubuntu 24.04** (Canonical)
4. Shape: Click "Change Shape"
   - Series: **Ampere (ARM)**
   - Shape: `VM.Standard.A1.Flex`
   - **OCPUs: 4** (max free)
   - **Memory: 24 GB** (max free)
5. Boot Volume: **200 GB**
6. Add your SSH public key (generate one if needed: `ssh-keygen -t ed25519`)
7. Click **Create** → wait ~2 minutes

Note your **Public IP address** (shown on instance page).

---

### 3. Open Required Ports

In Oracle Cloud: **Networking → Virtual Cloud Networks → Security Lists → Add Ingress Rules**

| Source | Protocol | Port | Note |
|--------|----------|------|------|
| 0.0.0.0/0 | TCP | 22 | SSH |
| 0.0.0.0/0 | TCP | 80 | HTTP |
| 0.0.0.0/0 | TCP | 443 | HTTPS |
| 0.0.0.0/0 | TCP | 8000 | Coolify (remove after setup) |

---

### 4. Set Up Phone Access

On your Android phone:

1. Install **Termux** from [F-Droid](https://f-droid.org/packages/com.termux/) (NOT Play Store)
2. Install **Tailscale** from [Play Store](https://play.google.com/store/apps/details?id=com.tailscale.ipn.android)
3. Open Termux:
   ```bash
   pkg install openssh
   ```

---

### 5. SSH Into Your Server

From Termux on your phone (or any terminal):

```bash
ssh ubuntu@YOUR_ORACLE_IP
```

---

### 6. Run the Setup Script

```bash
git clone https://github.com/YOUR_USERNAME/nexus.git
cd nexus
bash scripts/setup-oracle.sh
```

The script will:
- Install Docker, Node.js, Rust
- Install Coolify (deployment platform)
- Install OpenClaw (CEO agent runtime)
- Install Tailscale (secure access)
- Build and start ZeroClaw daemons (all 9 agents)
- Start all Docker services

**This takes about 10-15 minutes.**

---

### 7. Configure During Setup

When prompted during setup:

1. **Enter your GitHub repo URL** (where you cloned this)
2. **Configure `.env`** — the script will pause and ask you to fill in:
   - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather) on Telegram
   - `FOUNDER_TELEGRAM_ID` — from [@userinfobot](https://t.me/userinfobot)
   - `GOOGLE_API_KEY` — from [Google AI Studio](https://aistudio.google.com) (free)
   - `BASE_DOMAIN` — your domain name
   - Database passwords (generate random ones)
3. **Scan WhatsApp QR code** when prompted (for customer-facing support)

---

### 8. Wait for Completion

After ~10 minutes, you'll see:

```
========================================
 NEXUS Setup Complete!
========================================
Services running:
  OpenClaw gateway:  http://localhost:18789
  Coolify:           http://YOUR_IP:8000
...
```

---

### 9. Receive Welcome Message on Telegram

Check your Telegram. You should receive:

> 🦞 NEXUS is online. Your autonomous company is ready. Send 'status' to begin.

If you don't receive it within 2 minutes, check:
- `TELEGRAM_BOT_TOKEN` in your `.env`
- `FOUNDER_TELEGRAM_ID` is your numeric ID (not username)
- You started a chat with your bot (send `/start` to it first)

---

### 10. Reply: "status"

Send `status` to your Telegram bot. You should receive:

> Hey Yash! NEXUS is freshly online. 🟢
>
> 5 tasks queued for the ElevenLabs Clone MVP. 0 revenue yet (we haven't launched).
> All 9 agents are running. Watchdog is monitoring everything.
>
> Ready to build. Send 'Let's go' to start.

---

### 11. Start Building

Reply: `Let's go. Start building.`

The CEO agent will:
- Assign Task 1 (InsForge Schema) to the CTO agent
- CTO will open Claude Code and start building
- You'll receive updates automatically

---

### 12. Go About Your Day

Leave your phone. The company is running.

**12:00 PM** — You'll receive a midday update:
> Midday update: InsForge schema done ✅. CTO is 60% through the landing page.
> No blockers. ETA for live demo: 3 days. Anything you want to change?

Reply: `Looks good, keep going`

**6:00 PM** — You'll receive an evening summary:
> Evening summary: 2/5 MVP tasks complete today. Landing page nearly done.
> Tomorrow: finish landing page + start TTS API endpoint.
> No blockers. Revenue: $0 (pre-launch, as expected). Good night! 🌙

---

### 13. Your Company Is Running

That's it. From this point:

- **Morning briefings** arrive at 7 AM automatically
- **Send "build [feature]"** to add anything to the roadmap
- **Send "status"** anytime to get a full update
- **Send "money"** to check revenue
- **Send "ship"** to deploy
- **Respond "approve"** or **"reject"** when the CEO asks for decisions

The only thing you need to do is think about strategy and make decisions. Everything else is autonomous.

---

## File Structure

```
nexus/
├── CLAUDE.md               ← CEO agent instructions
├── PROJECT_BRIEF.md        ← Company overview
├── agents/                 ← Agent persona files
│   ├── ceo.md
│   ├── cto.md
│   ├── sales.md
│   └── ... (9 agents total)
├── products/
│   └── elevenlabs-clone/   ← Product #1
│       ├── SPEC.md         ← What we're building
│       ├── PLAN.md         ← Technical architecture
│       └── TASKS.md        ← Beads task queue
├── infrastructure/
│   ├── docker-compose.yml  ← All services
│   ├── openclaw-config.json5 ← Agent config + cron
│   └── .env.example        ← Copy to .env
├── scripts/
│   ├── setup-oracle.sh     ← One-command server setup
│   └── setup-windows.ps1   ← Windows CTO environment
├── telegram-commands/      ← OpenClaw skills
│   ├── status.md
│   ├── build.md
│   ├── ship.md
│   └── ... (9 commands)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   └── PROGRESS_LOG.md
└── .github/
    └── workflows/
        └── nexus-ci.yml    ← AI review + security scan + deploy
```

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Claude Max subscription | $100/mo |
| Oracle Cloud (4 OCPU, 24GB, 200GB) | $0 (always free) |
| All Docker services (self-hosted) | $0 |
| Gemini CLI, Groq, Ollama | $0 (free tiers) |
| **Total** | **$100/mo** |

Break-even: 6 customers on the Starter plan ($19/mo × 6 = $114/mo).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| CEO Agent | OpenClaw + Gemini 3.1 Pro |
| CTO Agent | Claude Code Max (Opus 4.6) |
| Background Agents | ZeroClaw + Groq/Gemini |
| Database | InsForge (PostgreSQL + S3) |
| Deployment | Coolify on Oracle Cloud ARM |
| Monitoring | Langfuse + GlitchTip + PostHog |
| Customer Support | Chatwoot (WhatsApp + Web) |
| CRM | Twenty |
| Automation | n8n |
| Search | Perplexica |
| Memory | Cognee |

---

## Product #1: NEXUS Voice Lab

ElevenLabs alternative — self-hosted TTS + voice cloning.

- 80+ voices (Kokoro, Apache 2.0)
- Voice cloning in 15 seconds (Chatterbox, Apache 2.0)
- ElevenLabs-compatible API (drop-in replacement)
- Free GPU via Kaggle notebooks
- Pricing: $0 / $19 / $49 / $199 per month

See `products/elevenlabs-clone/` for full spec and implementation plan.

---

## Help

Send your CEO agent a message. It will figure out what you need.

Or open an issue: [github.com/kayba-ai/nexus/issues](https://github.com/kayba-ai/nexus/issues)
