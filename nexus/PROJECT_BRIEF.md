# NEXUS — Project Brief

## Vision

NEXUS is an autonomous AI company controlled entirely from Telegram and WhatsApp. The founder (Yash) runs this company from his Android phone. He messages his CEO agent on Telegram, gives strategic direction, and the company builds, sells, and supports products autonomously.

## Core Principle

Everything flows through OpenClaw on Telegram/WhatsApp. The founder NEVER needs to open a terminal, IDE, or dashboard. He texts commands, receives progress updates, approves decisions, and reviews results — all from his messaging apps.

## Constraints

| Constraint | Value |
|-----------|-------|
| Hardware | Windows PC + Android phone, no GPU |
| Only paid service | Claude Max ($100/mo) — everything else free |
| Cloud | Oracle Cloud Free Tier (ARM, 24GB RAM, 200GB) |
| Primary interface | Telegram (founder) + WhatsApp (customers) |
| Secondary interface | Claude Code Web from phone for complex tasks |

## Company Stack

### Core Infrastructure
- **OpenClaw** — AI agent gateway, Telegram/WhatsApp bridge, CEO agent runtime
- **ZeroClaw** — Daemon runtime for background agents (Sales, Marketing, Support, etc.)
- **Coolify** — Self-hosted deployment platform (replaces Vercel/Heroku)
- **Oracle Cloud Free Tier** — ARM instance (4 OCPUs, 24GB RAM, 200GB disk)
- **Tailscale** — Secure remote access mesh network

### Services (all free, self-hosted)
- **InsForge** — Database + auth + S3-compatible storage (replaces Supabase)
- **Perplexica** — AI-powered web search (replaces Perplexity API)
- **n8n** — Workflow automation (replaces Zapier/Make)
- **Chatwoot** — Customer support inbox (replaces Intercom)
- **Twenty** — CRM (replaces HubSpot)
- **PostHog** — Product analytics (replaces Mixpanel)
- **GlitchTip** — Error monitoring (replaces Sentry)
- **Langfuse** — LLM observability + cost tracking (replaces Helicone)
- **Beads** — Task management for agents (replaces Linear/Jira)

### AI Models (all free except Claude Max)
- **Claude Max ($100/mo)** — Architecture, complex features (CTO agent)
- **Gemini 3.1 Pro (free)** — CEO, Marketing, Market Scout, Legal, Product Analyst
- **Groq Llama 4 (free)** — Sales, Finance, Watchdog (fast inference)
- **Ollama GLM-5 :cloud (free)** — Support, bulk tasks
- **Jules (free, 15/day)** — Dependency updates, test writing, maintenance

### Development Toolchain
- **SpecKit** — Spec-first development methodology
- **Continue CLI** — AI code review checks
- **Cognee** — Persistent knowledge graph (agent memory)
- **rtrvr.ai** — Lead scraping
- **Postiz** — Social media scheduling
- **Nano Banana** — Free AI image generation (via Gemini CLI)
- **NotebookLM CLI** — Audio briefing generation

## Product Roadmap

### Product #1: NEXUS Voice Lab (ElevenLabs Clone)
- **Why first:** Replaces our own ElevenLabs dependency ($22/mo → $0), clear market demand
- **MVP timeline:** 1–2 weeks
- **Revenue target:** $2,000 MRR in 90 days

### Product #2: Voice AI SaaS Platform (TBD)
- Built on Voice Lab infrastructure
- Telephony / AI phone agents

### Product #3: TBD
- Identified by Market Scout agent

## Success Metrics (90 days)

- [ ] Voice Lab live and processing payments
- [ ] $2,000+ MRR
- [ ] < $100/mo total infrastructure costs
- [ ] Founder spends < 30 min/day managing company
- [ ] All 9 agents running autonomously

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | CEO agent instructions |
| `docs/ARCHITECTURE.md` | System design |
| `docs/DECISIONS.md` | Decision log |
| `docs/PROGRESS_LOG.md` | Daily activity log |
| `docs/MARKET_INTEL.md` | Market research findings |
| `infrastructure/docker-compose.yml` | All services |
| `infrastructure/openclaw-config.json5` | Agent config + cron |
| `agents/*.md` | Agent persona files |
| `products/elevenlabs-clone/` | Product #1 |
