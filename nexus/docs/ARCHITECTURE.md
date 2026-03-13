# NEXUS — System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FOUNDER (Yash)                             │
│                    Android Phone / Telegram                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Telegram messages
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORACLE CLOUD ARM INSTANCE                        │
│                  (4 OCPUs, 24GB RAM, 200GB disk)                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    OpenClaw Gateway                          │   │
│  │         CEO Agent (Gemini 3.1 Pro)  :18789                  │   │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐                │   │
│  │    │ Telegram │  │WhatsApp  │  │Cron Jobs │                │   │
│  │    │  Bridge  │  │  Bridge  │  │ Scheduler│                │   │
│  │    └──────────┘  └──────────┘  └──────────┘                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│         Agent Mail (MCP) ────┼────────────────────────────────     │
│                              │                                      │
│  ┌────────────┐  ┌───────────┴──┐  ┌────────────┐  ┌──────────┐  │
│  │ ZeroClaw   │  │   ZeroClaw   │  │  ZeroClaw  │  │ZeroClaw  │  │
│  │   Sales    │  │  Marketing   │  │  Support   │  │  Scout   │  │
│  └────────────┘  └──────────────┘  └────────────┘  └──────────┘  │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ ZeroClaw   │  │   ZeroClaw   │  │  ZeroClaw  │  │ZeroClaw  │  │
│  │  Finance   │  │    Legal     │  │  Product   │  │Watchdog  │  │
│  └────────────┘  └──────────────┘  │  Analyst   │  └──────────┘  │
│                                     └────────────┘                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   Docker Compose Services                    │   │
│  │  InsForge │ Perplexica │ n8n │ Chatwoot │ Twenty │ PostHog  │   │
│  │  GlitchTip │ Langfuse │ Beads │ Cognee                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │  Claude Code (Max)  │
                    │    CTO Agent        │
                    │  Windows WSL2 /     │
                    │  Claude Code Web    │
                    └─────────────────────┘
```

## Data Flow

### Founder → Action
```
Founder texts Telegram
    → OpenClaw receives message
    → CEO agent interprets intent
    → Routes to appropriate skill or agent
    → Executes action
    → Responds to Telegram
```

### Build Workflow
```
"Build [feature]"
    → CEO creates SpecKit spec
    → CEO creates Beads tasks
    → CEO assigns to CTO via Agent Mail
    → CTO picks up task in Claude Code
    → CTO builds + tests + PRs
    → Continue CLI runs AI checks
    → GitHub Actions runs security scan
    → Coolify deploys on merge
    → CEO notifies founder
```

### Learning Loop (ACE Integration)
```
Customer interaction
    → Support agent handles via Chatwoot
    → PostHog tracks behavior
    → Product Analyst reviews weekly
    → Creates Beads improvement tasks
    → CEO decides which to prioritize
```

## Service Architecture

### Port Map

| Service | Port | Purpose |
|---------|------|---------|
| OpenClaw | 18789 | CEO agent gateway |
| InsForge | 8000 | DB + auth + storage |
| Perplexica | 3001 | AI web search |
| n8n | 5678 | Workflow automation |
| Chatwoot | 3000 | Customer support |
| Twenty CRM | 3002 | Sales CRM |
| PostHog | 8010 | Analytics |
| GlitchTip | 8080 | Error monitoring |
| Langfuse | 3003 | LLM observability |
| Coolify | 8443 | Deployment platform |

### Network Topology

```
Internet → Cloudflare Proxy → Oracle Cloud Public IP
                                        │
                    ┌───────────────────┤
                    │  Tailscale mesh   │
                    │  (founder access) │
                    └───────────────────┤
                                        │
                              Coolify reverse proxy
                              (SSL termination)
                                        │
                    ┌───────────────────┴──────────────────┐
                    │         Internal Docker network       │
                    │  All services communicate internally  │
                    └──────────────────────────────────────┘
```

## CTO Agent Architecture

The CTO is the only agent NOT running as a ZeroClaw daemon. It runs on:
1. **Primary:** Claude Code (Max) on Windows WSL2 — triggered by CEO via Agent Mail
2. **Secondary:** Claude Code Web from phone — for complex architecture sessions

### CTO Workflow
1. Receives task via Agent Mail MCP server
2. Searches Cognee for prior art and decisions
3. Uses SpecKit to create spec if missing
4. Implements using all available MCP servers
5. Writes tests before submitting PR
6. PR triggers Continue CLI AI checks
7. On CI pass: notifies CEO of completion

## Memory Architecture

```
Cognee Knowledge Graph
├── decisions/ — All architectural and product decisions
├── patterns/ — Successful code patterns and solutions
├── customers/ — Anonymized customer insights
├── market/ — Market research findings
├── agents/ — Agent learnings and improvements
└── costs/ — Cost patterns and optimization history
```

## Security Model

```
External Traffic
    → Cloudflare WAF (free tier)
    → SSL/TLS termination at Coolify
    → No direct port exposure (except 443/80)

Internal Access
    → Tailscale VPN for founder SSH access
    → All services internal-only (Docker network)
    → InsForge JWT for all API auth

Secrets Management
    → .env file on Oracle Cloud instance
    → Never in git (TruffleHog scan on every PR)
    → Coolify manages deployment env vars

Agent Security
    → Watchdog monitors all agent processes
    → Rate limits on all LLM calls (Langfuse)
    → Kill authority: Watchdog > CEO > any agent
```
