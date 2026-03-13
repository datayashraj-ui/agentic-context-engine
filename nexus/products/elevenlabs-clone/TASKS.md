# NEXUS Voice Lab — MVP Task Queue

**Project:** ElevenLabs Clone (NEXUS Voice Lab)
**Assigned to:** CTO Agent
**Status:** Ready to Start

---

## TASK-001: [SETUP] InsForge Database Schema

**Priority:** HIGH
**Depends on:** Nothing (start immediately)
**Assigned:** CTO
**Estimated:** 2-4 hours

### Description
Create all database tables in InsForge PostgreSQL for the Voice Lab product.

### Tables to Create

```sql
-- 1. Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    plan TEXT NOT NULL DEFAULT 'free',
    credits_remaining INTEGER NOT NULL DEFAULT 600,
    api_key TEXT UNIQUE DEFAULT encode(gen_random_bytes(32), 'hex'),
    stripe_customer_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Voices table (built-in + cloned)
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('builtin', 'cloned')),
    description TEXT,
    language TEXT DEFAULT 'en',
    preview_url TEXT,
    model_id TEXT NOT NULL,  -- internal reference (e.g., 'af_heart' for Kokoro)
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Generations table
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    voice_id UUID REFERENCES voices(id) NOT NULL,
    input_text TEXT NOT NULL,
    audio_url TEXT,
    duration_seconds DECIMAL(10,2),
    credits_used INTEGER,
    status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'complete', 'failed')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 4. Subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    stripe_subscription_id TEXT UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    plan TEXT NOT NULL CHECK (plan IN ('starter', 'pro', 'enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'trialing')),
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Also Create
- Indexes on: users.email, voices.user_id, generations.user_id, generations.created_at
- Row-level security policies for user data isolation
- InsForge S3 bucket: `nexus-voice-lab` with folders: `generations/`, `voice-clones/`
- Seed 20+ built-in Kokoro voices in voices table

### Acceptance Criteria
- [ ] All 4 tables created with correct schema
- [ ] Foreign key constraints working
- [ ] RLS policies applied (users can only see their own data)
- [ ] S3 bucket created
- [ ] 20+ built-in voices seeded
- [ ] Schema migration file committed to `backend/db/migrations/001_initial.sql`

---

## TASK-002: [FRONTEND] Landing Page

**Priority:** HIGH
**Depends on:** TASK-001 (for auth redirect)
**Assigned:** CTO
**Estimated:** 4-6 hours

### Description
Build the landing page for NEXUS Voice Lab. Mobile-first, converts visitors to signups.

### Sections Required

1. **Hero Section**
   - Headline: "Professional AI voices. Self-hosted. No data lock-in."
   - Sub: "ElevenLabs-compatible API. 80+ voices. Voice cloning. From $19/mo."
   - Primary CTA: "Try free — no credit card"
   - Secondary CTA: "View API docs"
   - Embedded audio demo: 5 voice samples the user can click to play

2. **Feature Grid** (3-column)
   - Text-to-Speech: "80+ voices, 32 languages, studio quality"
   - Voice Cloning: "Clone any voice in 15 seconds. Zero-shot."
   - API-First: "Drop-in ElevenLabs replacement. Change one URL."
   - Self-Hosted: "Your data stays on your server. GDPR ready."
   - Fast: "< 3 second generation. Priority queue on Pro."
   - Open Source: "Apache 2.0 license. Audit, extend, fork."

3. **Live Demo** (no account needed)
   - Text input (200 char limit for demo)
   - Voice dropdown (5 popular voices)
   - "Generate" button
   - Audio plays inline
   - Below: "Want more? Sign up free."

4. **Pricing Table**
   ```
   Free       Starter    Pro        Enterprise
   $0         $19/mo     $49/mo     $199/mo
   10 min     2 hrs      10 hrs     Unlimited
   1 clone    5 clones   Unlimited  Custom training
   No API     API ✓      API+       Self-hosted
   ```
   Each with CTA button and feature list.

5. **Footer**
   - Links: ToS, Privacy, API Docs, GitHub, Blog, Contact

### Tech Stack
- Next.js 15 App Router
- Tailwind CSS + shadcn/ui
- shadcn components: Button, Card, Tabs, Badge

### Acceptance Criteria
- [ ] All 5 sections implemented
- [ ] Mobile responsive (test at 375px, 768px, 1280px)
- [ ] Live demo works (calls backend TTS endpoint)
- [ ] Pricing CTAs link to signup with plan pre-selected
- [ ] Page load < 2 seconds (Lighthouse score > 85)
- [ ] ToS and Privacy pages linked (can be placeholder)

---

## TASK-003: [BACKEND] TTS Inference API

**Priority:** HIGH
**Depends on:** TASK-001
**Assigned:** CTO
**Estimated:** 6-8 hours

### Description
FastAPI service exposing ElevenLabs-compatible TTS endpoint with Kaggle GPU inference backend.

### Endpoint: POST /v1/text-to-speech/{voice_id}

```
Request:
  Header: Authorization: Bearer {jwt_token} OR X-API-Key: {api_key}
  Body: {
    "text": "Hello world",
    "model_id": "eleven_multilingual_v2",  // ignored, maps to our models
    "voice_settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }

Response:
  Content-Type: audio/mpeg
  Body: [binary audio stream]

  OR if async:
  Content-Type: application/json
  Body: {"generation_id": "uuid", "status": "queued"}
```

### Business Logic
1. Authenticate request (JWT or API key)
2. Look up voice (built-in or cloned?)
3. Check user credits (> 0 required)
4. Check Redis cache: hash(voice_id + text) → return cached if exists
5. Route to correct Kaggle endpoint:
   - `builtin` voice → Kaggle Kokoro server
   - `cloned` voice → Kaggle Chatterbox server
6. Call inference endpoint with retry (3 attempts, exponential backoff)
7. Store audio in InsForge S3
8. Deduct credits (1 credit per second of audio)
9. Return audio stream

### Rate Limiting
| Plan | Limit |
|------|-------|
| Free | 10 requests/min |
| Starter | 100 requests/min |
| Pro | 1000 requests/min |
| Enterprise | 10000 requests/min |

### Additional Endpoints
- `GET /v1/voices` — list all voices (built-in + user's clones)
- `GET /v1/voices/{voice_id}` — get voice details
- `POST /v1/voices/add` — upload 15-sec sample to create voice clone
- `GET /v1/models` — list models (return our models in ElevenLabs format)
- `GET /v1/user/subscription` — return plan + credits in ElevenLabs format

### Acceptance Criteria
- [ ] `/v1/text-to-speech/{voice_id}` returns audio stream
- [ ] ElevenLabs Python client works against our API (test this)
- [ ] Rate limiting enforced per plan
- [ ] Credits deducted correctly
- [ ] Redis caching working (second request is instant)
- [ ] Error handling: 401 (no auth), 402 (no credits), 429 (rate limit), 500 (inference fail)
- [ ] Unit tests for credit logic, caching, routing
- [ ] FastAPI auto-docs at /docs

---

## TASK-004: [FRONTEND] Dashboard

**Priority:** MEDIUM
**Depends on:** TASK-002, TASK-003
**Assigned:** CTO
**Estimated:** 6-8 hours

### Description
Authenticated dashboard for generating audio, browsing voices, and managing history.

### Layout
```
┌────────────┬─────────────────────────────────────────┐
│ Sidebar    │ Main Content                             │
│            │                                          │
│ Generate ← │ ← depends on selected nav item           │
│ Voices     │                                          │
│ History    │                                          │
│ Settings   │                                          │
│            │                                          │
│ Plan: Free │                                          │
│ 580 credits│                                          │
└────────────┴─────────────────────────────────────────┘
```

### Pages

**Generate Page (default)**
- Large text area (2000 char max, shows char count)
- Voice selector with search (dropdown showing 20+ voices with language tags)
- Speed slider (0.5x - 2.0x)
- Generate button (shows loading spinner)
- Audio player with: play/pause, progress bar, download button, share button
- "Save to History" checkbox (on by default)

**Voice Library Page**
- Grid of voice cards (name, language, description, preview play button)
- Tabs: "All Voices" / "My Clones"
- "Clone a Voice" button → opens upload modal
  - Drag-drop area for audio file (15-30 sec, WAV/MP3/M4A)
  - Name field for the clone
  - Requirements: clean audio, no music, no background noise
  - Progress bar during processing
- Search/filter by language

**History Page**
- Table: Date, Voice, Text (truncated), Duration, Audio player, Download
- Delete individual generations
- Bulk delete

**Settings Page**
- Profile (name, email)
- Plan & Billing (current plan, next billing date, upgrade CTA)
- API Key (show/regenerate)
- Usage (credits used this month, chart)
- Danger zone (delete account)

### Acceptance Criteria
- [ ] All 4 pages implemented
- [ ] Voice clone upload works end-to-end
- [ ] Audio player works on mobile (iOS + Android browser)
- [ ] Credits counter updates after generation
- [ ] History shows all past generations
- [ ] API key visible in Settings (can be copied)

---

## TASK-005: [PAYMENTS] Stripe Integration

**Priority:** MEDIUM
**Depends on:** TASK-001, TASK-002
**Assigned:** CTO
**Estimated:** 4-5 hours

### Description
Stripe Checkout for subscription plans, webhook handler, and credit system.

### Stripe Products to Create
```
Product: NEXUS Voice Lab Starter
  Price ID: price_starter_monthly
  Amount: $1900 (= $19.00)
  Interval: month

Product: NEXUS Voice Lab Pro
  Price ID: price_pro_monthly
  Amount: $4900 (= $49.00)
  Interval: month

Product: NEXUS Voice Lab Enterprise
  Price ID: price_enterprise_monthly
  Amount: $19900 (= $199.00)
  Interval: month
```

### Credit Allocation by Plan
| Plan | Monthly Credits |
|------|----------------|
| Free | 600 (10 min) |
| Starter | 7200 (2 hrs) |
| Pro | 36000 (10 hrs) |
| Enterprise | 999999 (unlimited) |

### Checkout Flow
1. User clicks pricing tier CTA
2. Redirect to Stripe Checkout (hosted page)
3. Stripe Checkout handles card entry
4. On success: webhook fires `checkout.session.completed`
5. Backend: create subscription record, update user plan + credits
6. Redirect to dashboard with success message

### Webhook Events to Handle
| Event | Action |
|-------|--------|
| `checkout.session.completed` | Activate subscription, add credits |
| `invoice.paid` | Monthly credit top-up |
| `invoice.payment_failed` | Send email, update status to `past_due` |
| `customer.subscription.deleted` | Downgrade to free, remove credits above free limit |
| `customer.subscription.updated` | Update plan (upgrade/downgrade) |

### Acceptance Criteria
- [ ] Starter ($19/mo) checkout works end-to-end
- [ ] Credits added to user account after payment
- [ ] Webhook signature verified (using `STRIPE_WEBHOOK_SECRET`)
- [ ] Subscription cancellation downgrades user correctly
- [ ] Monthly renewal tops up credits
- [ ] Billing page in Settings shows plan + next billing date
- [ ] Stripe webhook tests pass (use Stripe CLI for local testing)
- [ ] Unit tests for credit top-up logic
