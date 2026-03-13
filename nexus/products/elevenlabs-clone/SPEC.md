# NEXUS Voice Lab — Product Specification

**Version:** 1.0
**Status:** In Development
**Target Launch:** 2 weeks from kickoff
**Product Owner:** NEXUS CEO

---

## Overview

NEXUS Voice Lab is a self-hosted, open-source ElevenLabs alternative. It provides high-quality text-to-speech and voice cloning through a clean web dashboard and API-compatible endpoints.

Architecture inspired by: github.com/Andreaswt/elevenlabs-clone
Adapted for: zero-GPU local development with free cloud GPU inference.

---

## What It Does

### Core Features

| Feature | Description | Model |
|---------|-------------|-------|
| Text-to-Speech | Generate natural speech from text | Kokoro (80+ voices) |
| Voice Cloning | Clone any voice from 15-second sample | Chatterbox zero-shot |
| Voice Library | 80+ built-in + user uploaded clones | Kokoro built-ins |
| Multi-language | 32+ languages | Kokoro multilingual |
| API-first | ElevenLabs-compatible REST API | — |
| Dashboard | Web UI for generate/play/download | Next.js 15 |

### ElevenLabs API Compatibility

Drop-in replacement for ElevenLabs endpoints:

```
POST /v1/text-to-speech/{voice_id}              ← same as ElevenLabs
GET  /v1/voices                                   ← same as ElevenLabs
GET  /v1/voices/{voice_id}                        ← same as ElevenLabs
POST /v1/voices/add                               ← voice cloning endpoint
GET  /v1/models                                   ← list available models
GET  /v1/user/subscription                        ← plan/credits info
```

Developers can replace `https://api.elevenlabs.io` with `https://api.yourdomain.com`
and everything works — no code changes required.

---

## Tech Stack

### Frontend
- **Framework:** Next.js 15 (App Router)
- **UI:** React 19 + Tailwind CSS + shadcn/ui
- **State:** Zustand for client state
- **Audio:** Web Audio API for playback

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Async:** asyncio + httpx for non-blocking inference calls
- **Queue:** Redis (InsForge) for job queuing
- **API Docs:** Auto-generated via FastAPI /docs

### AI/ML Models
| Model | Purpose | License | Source |
|-------|---------|---------|--------|
| Kokoro | TTS, 80+ voices, 32 languages | Apache 2.0 | HuggingFace |
| Chatterbox-Turbo | Voice cloning (zero-shot, 15s sample) | Apache 2.0 | Resemble AI |

### Infrastructure
| Layer | Service | Cost |
|-------|---------|------|
| Database | InsForge PostgreSQL | $0 (self-hosted) |
| Auth | InsForge JWT + OAuth | $0 |
| Storage | InsForge S3-compatible | $0 |
| Job Queue | n8n webhooks | $0 |
| Deployment | Docker on Coolify (Oracle Cloud) | $0 |
| GPU Inference | Kaggle Notebooks (T4 GPU) | $0 |
| Payments | Stripe | 2.9% + $0.30 per transaction |

---

## How It Works Without a GPU

The Oracle Cloud ARM instance has no GPU. Here's how inference works:

```
User submits text + voice_id
    │
    ▼
FastAPI backend receives request
    │
    ▼
Check Redis cache — already generated? → Return cached audio
    │
    ▼ (cache miss)
Determine model needed:
    ├─ Built-in voice → Call Kaggle/Kokoro endpoint
    └─ Cloned voice → Call Kaggle/Chatterbox endpoint
    │
    ▼
Kaggle notebook (free T4 GPU) processes inference
Returns audio/mpeg in 1-3 seconds
    │
    ▼
Store in InsForge S3 (cache + permanent if user saves)
    │
    ▼
Return audio stream to user
```

### Kaggle Notebook Setup
- One persistent Kaggle notebook per model (Kokoro, Chatterbox)
- Notebooks run as Flask API servers listening for inference requests
- Kaggle provides ~30 hours/week free T4 GPU per account
- Multiple Kaggle accounts for redundancy
- Session pre-warming via cron (keeps notebooks warm between requests)
- Fallback to Colab if Kaggle quota exhausted

---

## Pricing

| Plan | Price | Limits | API |
|------|-------|--------|-----|
| Free | $0/mo | 10 min audio/mo, 1 voice clone | No |
| Starter | $19/mo | 2 hours audio/mo, 5 clones | Yes |
| Pro | $49/mo | 10 hours audio/mo, unlimited clones | Yes (priority queue) |
| Enterprise | $199/mo | Unlimited, self-hosted Docker image, custom training, SLA | Yes |

**Credit system:** 1 credit = 1 second of generated audio
Plans top up credits on payment. Credits decrement on generation.

---

## Why Product #1

1. **Immediate ROI:** Replaces our own ElevenLabs dependency ($22/mo → $0, saves $264/year)
2. **Proven market:** $4.1B voice AI market, 2,400+ monthly searches for "elevenlabs alternative"
3. **Zero switching friction:** Drop-in API = developers switch without changing code
4. **Open source differentiator:** Data sovereignty, customization, no vendor lock-in
5. **Foundation for Product #2:** Voice AI SaaS platform (telephony/AI phone agents) built on this
6. **Feasible solo build:** All models are Apache 2.0, well-documented, active communities

---

## Acceptance Criteria (MVP)

### Must Have (v1.0)
- [ ] User can sign up, log in, and manage account
- [ ] User can browse 20+ built-in voices with audio preview
- [ ] User can type text, select voice, click Generate, hear result
- [ ] User can download generated audio as MP3
- [ ] User can upload 15-second sample to clone a voice
- [ ] API endpoint compatible with ElevenLabs format
- [ ] Stripe payment for Starter plan ($19/mo)
- [ ] Credit system accurately tracks usage
- [ ] Works on mobile (responsive)

### Nice to Have (v1.1)
- [ ] Batch generation (multiple texts at once)
- [ ] Voice settings (stability, similarity boost)
- [ ] History page with all past generations
- [ ] API key management
- [ ] Team accounts / shared voice library

---

## Security Requirements

- All API endpoints require auth (JWT or API key)
- File uploads validated: audio only, max 10MB, wav/mp3/m4a
- Rate limiting per user based on plan
- No user audio stored longer than 30 days (unless explicitly saved)
- GDPR-compliant: users can delete all their data
