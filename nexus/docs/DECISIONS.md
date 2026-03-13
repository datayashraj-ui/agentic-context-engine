# NEXUS — Decision Log

Format: `[DATE] [AGENT] [CONFIDENCE] Decision | Rationale | Outcome`

---

## 2026-03-13 — Bootstrap Decisions

### ARCH-001: Oracle Cloud Free Tier as primary infrastructure
- **Agent:** CEO (Founder input)
- **Confidence:** 95%
- **Decision:** Use Oracle Cloud ARM instance (4 OCPUs, 24GB RAM) as sole server
- **Rationale:** Only cloud provider offering always-free ARM instances with this spec. No monthly cost vs $50-100/mo for equivalent Hetzner/DigitalOcean.
- **Outcome:** Pending deployment
- **Cognee tags:** infrastructure, cost-optimization

### ARCH-002: OpenClaw as primary agent runtime
- **Agent:** CEO (Founder input)
- **Confidence:** 90%
- **Decision:** Use OpenClaw for CEO agent and Telegram/WhatsApp integration
- **Rationale:** Purpose-built for conversational AI agents with messaging integrations. Supports cron jobs, skill system, multi-channel.
- **Outcome:** Pending deployment
- **Cognee tags:** infrastructure, agents

### ARCH-003: InsForge for database/auth/storage
- **Agent:** CEO (Founder input)
- **Confidence:** 88%
- **Decision:** Use InsForge instead of Supabase/PlanetScale/Cloudflare R2
- **Rationale:** Single service replaces three separate services. Self-hosted = no cost. Compatible APIs with standard PostgreSQL + S3.
- **Outcome:** Pending deployment
- **Cognee tags:** infrastructure, database

### ARCH-004: ElevenLabs Clone as Product #1
- **Agent:** CEO (Founder input)
- **Confidence:** 85%
- **Decision:** Build self-hosted voice TTS/cloning as first product
- **Rationale:** (1) Replaces $22/mo ElevenLabs subscription immediately. (2) $4.1B market, proven demand. (3) Drop-in API compatibility lowers switching friction. (4) Ships in 1-2 weeks with open-source models.
- **Outcome:** In progress
- **Cognee tags:** product, voice-ai, revenue

### ARCH-005: Kaggle/Colab notebooks for GPU inference
- **Agent:** CTO
- **Confidence:** 80%
- **Decision:** Use free Kaggle T4 notebooks as GPU backend for TTS inference
- **Rationale:** No local GPU available. Kaggle provides free T4/P100 GPUs. Alternative to renting GPU cloud ($0.50-2.00/hr).
- **Tradeoffs:** Latency higher (1-3s cold start), session limits apply
- **Outcome:** Pending implementation
- **Cognee tags:** product, infrastructure, gpu

---

## Template for New Decisions

```
### [ID]: [Short title]
- **Agent:** [Who made the decision]
- **Confidence:** [%]
- **Decision:** [What was decided]
- **Rationale:** [Why]
- **Tradeoffs:** [What was given up]
- **Outcome:** [Pending / Success / Failed / Revised]
- **Cognee tags:** [tags for knowledge graph]
```
