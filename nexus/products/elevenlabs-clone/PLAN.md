# NEXUS Voice Lab — Technical Architecture Plan

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NEXUS VOICE LAB                                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              FRONTEND (Next.js 15)                            │  │
│  │                                                               │  │
│  │  Landing Page → Signup → Dashboard → Voice Library           │  │
│  │  Generate UI → History → Voice Clone Upload → Settings        │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                            │ HTTPS                                  │
│  ┌─────────────────────────▼────────────────────────────────────┐  │
│  │              BACKEND API (FastAPI)                            │  │
│  │                                                               │  │
│  │  /v1/text-to-speech/{voice_id}  ElevenLabs-compatible        │  │
│  │  /v1/voices              GET voices list                      │  │
│  │  /v1/voices/add          POST voice clone                     │  │
│  │  /internal/generate      Internal queue endpoint              │  │
│  │  /webhooks/stripe        Payment events                       │  │
│  └──────┬──────────────┬───────────────────────────────────────-┘  │
│         │              │                                            │
│  ┌──────▼──────┐  ┌────▼──────────────────────────────────────┐   │
│  │  InsForge   │  │           Job Queue (Redis/n8n)             │   │
│  │  PostgreSQL │  │                                             │   │
│  │  S3 Storage │  │  Generation jobs → GPU workers              │   │
│  │  Auth/JWT   │  │  Voice clone jobs → Chatterbox worker       │   │
│  └─────────────┘  └────┬──────────────────────────────────────-┘   │
│                        │ HTTPS                                      │
└────────────────────────┼────────────────────────────────────────────┘
                         │ Inference requests
         ┌───────────────┼─────────────────┐
         │               │                 │
┌────────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
│   Kaggle #1   │  │  Kaggle #2  │  │   Colab FB  │
│ Kokoro (TTS)  │  │ Chatterbox  │  │ (Fallback)  │
│ Flask :5000   │  │ Flask :5000  │  │             │
│ Free T4 GPU   │  │ Free T4 GPU  │  │             │
└───────────────┘  └─────────────┘  └─────────────┘
```

## Directory Structure

```
products/elevenlabs-clone/
├── frontend/                      # Next.js 15 app
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/page.tsx      # Main generation UI
│   │   │   ├── voices/page.tsx         # Voice library
│   │   │   ├── history/page.tsx        # Past generations
│   │   │   └── settings/page.tsx       # Account, billing, API keys
│   │   ├── page.tsx                    # Landing page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components
│   │   ├── voice-card.tsx          # Voice preview card
│   │   ├── generate-form.tsx       # TTS generation form
│   │   ├── audio-player.tsx        # Custom audio player
│   │   ├── voice-clone-upload.tsx  # 15-sec audio upload
│   │   └── pricing-table.tsx       # Pricing tiers
│   └── lib/
│       ├── api.ts                  # API client
│       └── auth.ts                 # InsForge auth helpers
│
├── backend/                       # FastAPI Python app
│   ├── main.py
│   ├── routes/
│   │   ├── tts.py             # /v1/text-to-speech endpoints
│   │   ├── voices.py          # /v1/voices endpoints
│   │   ├── auth.py            # JWT + OAuth
│   │   ├── billing.py         # Stripe endpoints
│   │   └── webhooks.py        # Stripe webhook handler
│   ├── services/
│   │   ├── inference.py       # GPU inference calls (Kaggle)
│   │   ├── credits.py         # Credit system logic
│   │   ├── storage.py         # InsForge S3 operations
│   │   └── queue.py           # Redis job queue
│   ├── models/
│   │   ├── user.py
│   │   ├── voice.py
│   │   └── generation.py
│   └── db/
│       ├── schema.sql         # InsForge PostgreSQL schema
│       └── migrations/
│
├── kaggle-notebooks/          # GPU inference servers
│   ├── kokoro-server.ipynb    # Kokoro TTS Flask server
│   └── chatterbox-server.ipynb # Chatterbox Flask server
│
├── docker-compose.yml         # Frontend + Backend containers
└── nginx.conf                 # Reverse proxy config
```

## Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    plan TEXT NOT NULL DEFAULT 'free',  -- free, starter, pro, enterprise
    credits_remaining INTEGER NOT NULL DEFAULT 600,  -- 10 min = 600 sec
    api_key TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Voices (built-in + cloned)
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'builtin' | 'cloned'
    description TEXT,
    language TEXT DEFAULT 'en',
    sample_url TEXT,      -- preview audio URL
    model_ref TEXT,       -- internal model identifier
    user_id UUID REFERENCES users(id),  -- NULL for builtin
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generations
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    voice_id UUID REFERENCES voices(id) NOT NULL,
    input_text TEXT NOT NULL,
    audio_url TEXT,       -- S3 URL when complete
    duration_seconds DECIMAL(10,2),
    credits_used INTEGER,
    status TEXT DEFAULT 'queued',  -- queued, processing, complete, failed
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    stripe_subscription_id TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    plan TEXT NOT NULL,  -- starter, pro, enterprise
    status TEXT NOT NULL,  -- active, canceled, past_due
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Inference Architecture

### Request Flow (normal, cached)
```
POST /v1/text-to-speech/21m00Tcm4TlvDq8ikWAM
{text: "Hello world", model_id: "eleven_multilingual_v2"}

1. Validate JWT / API key
2. Check user credits (> 0?)
3. Hash(text + voice_id) → check Redis cache
4. Cache hit? → return cached audio URL (< 50ms)
5. Cache miss → enqueue job
6. Return job_id immediately (or stream)
```

### Inference Job
```
Redis Queue → Worker picks up job
1. Determine voice type (builtin → Kokoro, cloned → Chatterbox)
2. Select available Kaggle endpoint (health check first)
3. POST to Kaggle Flask server: {text, voice_ref, settings}
4. Stream response audio bytes
5. Store in InsForge S3: generations/{user_id}/{generation_id}.mp3
6. Update DB: status=complete, audio_url, duration_seconds
7. Deduct credits from user
8. Notify frontend (WebSocket or polling)
```

### Kaggle Notebook Server (kokoro-server.ipynb)
```python
# Runs inside Kaggle notebook, exposes Flask API
from flask import Flask, request, send_file
from kokoro import KPipeline

app = Flask(__name__)
pipeline = KPipeline(lang_code='a')  # auto language

@app.route('/tts', methods=['POST'])
def generate():
    data = request.json
    text = data['text']
    voice = data['voice']  # e.g., 'af_heart'

    audio_data = pipeline(text, voice=voice, speed=1.0)
    # Returns audio bytes as MP3
    return send_file(audio_data, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Kaggle provides a public HTTPS URL for each running notebook.

## Frontend Architecture

### Landing Page Sections
1. **Hero** — Headline + embedded audio player demo + "Try free" CTA
2. **Features grid** — TTS / Voice Cloning / API-first / 80+ Voices / 32 Languages
3. **Live demo** — Text input + voice dropdown, generate without account
4. **API comparison** — Side-by-side with ElevenLabs API (identical format)
5. **Pricing table** — Free / $19 / $49 / $199 with feature comparison
6. **Testimonials** — (placeholder until we have real ones)
7. **Footer** — ToS, Privacy, GitHub, API docs

### Dashboard Layout
```
Sidebar:
  - Generate (main)
  - Voice Library
  - History
  - Settings

Main area (Generate):
  - Text input (large textarea, 5000 char max)
  - Voice selector (dropdown with search)
  - Generate button
  - Audio player (appears after generation)
  - Download + Share buttons
  - Remaining credits indicator
```

## Authentication Flow

```
InsForge handles auth:
1. Sign up with email → InsForge creates user + JWT
2. OAuth (Google) → InsForge OAuth handler
3. JWT stored in httpOnly cookie (not localStorage)
4. API key: generated on demand in Settings → shown once
5. API key auth: X-API-Key header on /v1/* endpoints
```

## Deployment (Docker Compose)

```yaml
services:
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.voicelab.yourdomain.com
      - INSFORGE_URL=http://insforge:8000
    ports:
      - "3004:3000"

  backend:
    build: ./backend
    environment:
      - INSFORGE_URL=http://insforge:8000
      - REDIS_URL=redis://insforge-redis:6379
      - KAGGLE_KOKORO_URL=${KAGGLE_KOKORO_URL}
      - KAGGLE_CHATTERBOX_URL=${KAGGLE_CHATTERBOX_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    ports:
      - "8002:8000"
```

Coolify handles SSL, domain routing, and zero-downtime deploys.

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Kaggle session expires | Pre-warm cron every 6 hours, 3 fallback accounts |
| Kaggle quota exhausted | Colab fallback + notify CEO |
| GPU OOM on large text | Chunk text at 500 chars, process in parallel |
| S3 storage fills up | 30-day auto-delete for unsaved generations |
| API abuse | Rate limiting (100 req/hour on free, 1000/hour on paid) |
| Voice clone of celebrities | Terms of Service + content policy flag |
