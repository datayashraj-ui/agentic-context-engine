# Pipecat Voice Orchestration Integration

## Why Pipecat?

Pipecat is a **production-ready framework** for building voice AI agents that handles the complexity of:
- Real-time audio streaming
- Turn detection and interruption handling
- Multi-modal processing (audio + vision)
- Transport layer abstraction (WebRTC, WebSocket, etc.)
- 40+ service integrations

**vs. Building Custom**:
- ❌ Custom: Months of development for edge cases
- ✅ Pipecat: Days to production with battle-tested code

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        PIPECAT VOICE PIPELINE                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   TRANSPORT │───▶│     STT     │───▶│     LLM     │                 │
│  │  (WebRTC)   │    │  (Indic)    │    │  (Ollama)   │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         │                                       │                        │
│         │                                       ▼                        │
│         │            ┌─────────────┐    ┌─────────────┐                 │
│         │            │   VISION    │◀───│     TTS     │                 │
│         │            │  (Optional) │    │  (Indic)    │                 │
│         │            └─────────────┘    └─────────────┘                 │
│         │                   │                   │                        │
│         │                   ▼                   │                        │
│         │            ┌─────────────────────────┐│                        │
│         └───────────▶│    FRAME PROCESSOR      ││                        │
│                      │  (Interruption, VAD)    ││                        │
│                      └─────────────────────────┘│                        │
│                                                 │                        │
│                      ┌─────────────────────────┐│                        │
│                      │    CONTEXT MANAGER      ││                        │
│                      │  (Conversation State)   ││                        │
│                      └─────────────────────────┘│                        │
│                                                 │                        │
└─────────────────────────────────────────────────┘                        │
```

---

## Implementation

### 1. Install Pipecat

```bash
pip install pipecat-ai[daily,openai]
# For Indian language support
pip install transformers torch torchaudio
```

### 2. Core Pipeline

```python
# voice/pipecat_pipeline.py
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from pipecat.frames.frames import (
    Frame,
    AudioRawFrame,
    TextFrame,
    LLMMessagesFrame,
    EndFrame
)

import asyncio
from typing import Optional

# Custom Indic TTS/STT services
from .indic_tts_service import IndicTTSService
from .indic_stt_service import IndicSTTService


class GodCodeVoiceAgent:
    """
    Production voice agent using Pipecat

    Features:
    - Real-time streaming audio
    - Interruption handling (barge-in)
    - Voice Activity Detection (VAD)
    - Multi-speaker support
    - Context preservation
    """

    def __init__(
        self,
        room_url: str,
        token: str,
        bot_name: str = "God Code Assistant",
        language: str = "hindi"
    ):
        self.room_url = room_url
        self.token = token
        self.bot_name = bot_name
        self.language = language

        # Initialize services
        self._init_services()

    def _init_services(self):
        """Initialize Pipecat services"""

        # Transport (WebRTC via Daily.co)
        self.transport = DailyTransport(
            self.room_url,
            self.token,
            self.bot_name,
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                video_out_enabled=False,  # Audio-only for now
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer()
            )
        )

        # STT (Indic languages)
        self.stt = IndicSTTService(language=self.language)

        # LLM (Ollama via OpenAI-compatible API)
        self.llm = OpenAILLMService(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            model="qwen2.5:7b"
        )

        # TTS (Indic languages)
        self.tts = IndicTTSService(
            language=self.language,
            voice_description="professional female with clear articulation"
        )

    async def run(self):
        """Run the voice pipeline"""

        # Build pipeline
        pipeline = Pipeline([
            self.transport.input(),   # Get audio input
            self.stt,                  # Speech to text
            self.llm,                  # Generate response
            self.tts,                  # Text to speech
            self.transport.output()    # Send audio output
        ])

        # Create task
        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,  # Enable barge-in
                enable_metrics=True,
                enable_usage_metrics=True
            )
        )

        # Run pipeline
        runner = PipelineRunner()
        await runner.run(task)


# Custom Indic TTS Service for Pipecat
class IndicTTSService:
    """
    Pipecat-compatible TTS service using AI4Bharat Indic Parler-TTS
    """

    def __init__(self, language: str = "hindi", voice_description: str = "professional female"):
        from transformers import AutoModel
        import torch

        self.language = language
        self.voice_description = voice_description

        # Load model
        self.model = AutoModel.from_pretrained(
            "ai4bharat/indic-parler-tts",
            trust_remote_code=True
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    async def run_tts(self, text: str) -> AudioRawFrame:
        """
        Convert text to speech

        Args:
            text: Text to synthesize

        Returns:
            AudioRawFrame with synthesized speech
        """
        description = f"{self.voice_description} speaker delivers speech in {self.language}"

        # Generate audio
        audio = self.model.generate(text, description)

        # Convert to AudioRawFrame for Pipecat
        return AudioRawFrame(
            audio=audio.numpy().tobytes(),
            sample_rate=24000,
            num_channels=1
        )

    async def process_frame(self, frame: Frame, direction):
        """Pipecat frame processor interface"""
        if isinstance(frame, TextFrame):
            # Convert text to audio
            audio_frame = await self.run_tts(frame.text)
            yield audio_frame
        else:
            yield frame


# Custom Indic STT Service for Pipecat
class IndicSTTService:
    """
    Pipecat-compatible STT service using AI4Bharat IndicConformer
    """

    def __init__(self, language: str = "hindi"):
        from transformers import AutoModel

        self.language = language

        # Load model
        self.model = AutoModel.from_pretrained(
            "ai4bharat/indic-conformer-600m-multilingual",
            trust_remote_code=True
        )

    async def run_stt(self, audio: AudioRawFrame) -> str:
        """
        Convert speech to text

        Args:
            audio: Audio frame

        Returns:
            Transcribed text
        """
        # Convert audio frame to format for model
        import numpy as np
        audio_array = np.frombuffer(audio.audio, dtype=np.int16)

        # Transcribe
        text = self.model.transcribe(audio_array, self.language)

        return text

    async def process_frame(self, frame: Frame, direction):
        """Pipecat frame processor interface"""
        if isinstance(frame, AudioRawFrame):
            # Convert audio to text
            text = await self.run_stt(frame)
            yield TextFrame(text=text)
        else:
            yield frame
```

### 3. Integration with God Code

```python
# god_code/voice_interface.py
from voice.pipecat_pipeline import GodCodeVoiceAgent

class VoiceEnabledCodingSession:
    """
    Voice-enabled coding session using Pipecat

    Features:
    - Voice commands: "Create a function...", "Fix this bug...", "Explain this code..."
    - Code reading: AI reads code back to you
    - Multi-speaker meetings: Pair programming with AI
    - Interruption handling: Stop AI mid-sentence
    """

    def __init__(self):
        self.voice_agent = None
        self.session_active = False

    async def start_voice_session(self, room_url: str, token: str):
        """Start voice coding session"""
        self.voice_agent = GodCodeVoiceAgent(
            room_url=room_url,
            token=token,
            bot_name="God Code Assistant",
            language="english"  # or "hindi", "tamil", etc.
        )

        self.session_active = True
        await self.voice_agent.run()

    async def voice_command(self, command: str) -> str:
        """
        Execute voice command

        Examples:
        - "Create a Python function to sort a list"
        - "Fix the bug on line 42"
        - "Explain what this code does"
        - "Run the tests"
        """
        # Process command through God Code backend
        # Return response via voice

        pass

    async def read_code(self, file_path: str):
        """Read code file out loud"""
        # Read file
        # Synthesize with TTS
        # Stream to voice agent

        pass
```

### 4. WebRTC Setup (Using Daily.co)

```python
# scripts/create_voice_room.py
import requests
import os

DAILY_API_KEY = os.getenv("DAILY_API_KEY")  # Get from daily.co

def create_room(room_name: str) -> dict:
    """Create Daily.co room for voice session"""

    response = requests.post(
        "https://api.daily.co/v1/rooms",
        headers={
            "Authorization": f"Bearer {DAILY_API_KEY}"
        },
        json={
            "name": room_name,
            "properties": {
                "enable_screenshare": False,
                "enable_chat": True,
                "start_video_off": True,
                "start_audio_off": False,
                "exp": 3600  # 1 hour expiry
            }
        }
    )

    return response.json()

# Usage:
room = create_room("godcode-session-123")
print(f"Room URL: {room['url']}")
print(f"Join at: {room['url']}")
```

---

## Advanced Features

### 1. Multi-Speaker Support

```python
# Multiple AI employees in voice meeting
employees = [
    ("Priya", "hindi", "professional female"),
    ("Rahul", "hindi", "energetic male"),
    ("Anita", "english", "analytical female")
]

for name, lang, voice in employees:
    agent = GodCodeVoiceAgent(
        room_url=room_url,
        token=token,
        bot_name=name,
        language=lang
    )
    # Each employee joins the same room
```

### 2. Vision + Voice (Multimodal)

```python
# See screen + hear voice
from pipecat.services.openai import OpenAIVisionService

vision = OpenAIVisionService()

pipeline = Pipeline([
    transport.input(),
    stt,
    vision,  # Analyzes screen
    llm,     # Uses both audio transcript + vision
    tts,
    transport.output()
])

# "What's on my screen?" → AI sees and responds
```

### 3. Interruption Handling

```python
# User can interrupt AI mid-sentence
params = PipelineParams(
    allow_interruptions=True,
    enable_metrics=True,
    # When user speaks, AI stops immediately
)
```

### 4. Context Preservation

```python
# Maintain conversation history
from pipecat.services.conversation import ConversationService

conversation = ConversationService()

pipeline = Pipeline([
    transport.input(),
    stt,
    conversation,  # Adds context
    llm,
    tts,
    transport.output()
])

# "Create a function" → context from previous conversation
```

---

## Production Deployment

### Option 1: Self-Hosted (Free)

```yaml
# docker-compose.yml
version: '3.8'

services:
  godcode-voice:
    build: .
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - DAILY_API_KEY=${DAILY_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

### Option 2: Cloud Deployment

```python
# Deploy to Railway/Render/Fly.io
# Automatic HTTPS + WebRTC handling
```

---

## Pipecat vs Custom Implementation

| Feature | Custom Build | Pipecat |
|---------|-------------|---------|
| **Development Time** | 3-6 months | 1-2 weeks |
| **WebRTC Setup** | Complex | Built-in |
| **Interruption Handling** | Manual implementation | Automatic |
| **VAD Integration** | Custom | Silero included |
| **Transport Options** | Limited | WebRTC, WebSocket, PSTN |
| **Multi-modal** | Hard to add | Built-in |
| **Production Ready** | Extensive testing needed | Battle-tested |
| **Cost** | High (dev time) | Free (open-source) |

---

## Indian Language Support

All 21 languages supported:
- Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese
- Urdu, Kashmiri, Sanskrit, Nepali, Konkani, Manipuri, Bodo, Dogri, Santali, Sindhi

**With 69 voice variants and 10 emotions** (happy, sad, angry, etc.)

---

## Next Steps

1. ✅ Install Pipecat: `pip install pipecat-ai`
2. ✅ Create Daily.co account (free tier)
3. ✅ Implement IndicTTSService and IndicSTTService
4. ✅ Test with simple pipeline
5. ✅ Integrate with God Code backend

**Result**: Production-ready voice coding assistant in days, not months! 🎤
