# Unified AI Workspace
## ACE Prompt Engineering + Universal AI Dashboard

**Production-ready, open-source, fully local AI system combining intelligent prompt engineering with autonomous AI workforce management.**

---

## 🎯 Overview

This unified system combines two powerful AI architectures:

### **System 1: ACE Prompt Engineering Architect**
Multi-role LLM system that generates optimized prompts through:
- **6-step interactive dialogue** with requirement gathering
- **Multi-agent architecture** (Analyzer, Generator, Validator, Reflector, Skill Manager)
- **SQLite skillbook** with semantic search for pattern reuse
- **Learning loop** that improves from user feedback

### **System 2: Universal AI Workspace Dashboard**
Complete AI workforce with:
- **Department structure** (Sales, Marketing, Operations, Customer Success, R&D, Developers)
- **AI employees** with unique personalities and voices
- **Meeting room** for multi-agent collaboration
- **Voice pipeline** with Indian language support (21 languages, 69 voices)
- **Browser automation** for deployment and integration
- **Real-time dashboard** for monitoring and metrics

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          UNIFIED AI WORKSPACE                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────┐       ┌─────────────────────────────────┐   │
│  │   SYSTEM 1: ACE PROMPT     │       │   SYSTEM 2: AI WORKSPACE        │   │
│  │   ENGINEERING ARCHITECT    │       │   DASHBOARD                     │   │
│  ├────────────────────────────┤       ├─────────────────────────────────┤   │
│  │                            │       │                                 │   │
│  │  ┌──────────────────┐     │       │  ┌──────────────────────────┐  │   │
│  │  │  Analyzer Agent  │     │       │  │  Factory Manager         │  │   │
│  │  │  Generator Agent │     │       │  │  ├─ Sales Dept          │  │   │
│  │  │  Validator Agent │     │       │  │  ├─ Marketing Dept      │  │   │
│  │  │  Reflector Agent │     │       │  │  ├─ Operations Dept     │  │   │
│  │  │  Skill Manager   │     │       │  │  ├─ Customer Success    │  │   │
│  │  └──────────────────┘     │       │  │  ├─ Developers Team     │  │   │
│  │          ▼                 │       │  │  └─ R&D Department      │  │   │
│  │  ┌──────────────────┐     │       │  └──────────────────────────┘  │   │
│  │  │  SQLite Skillbook│     │       │          ▼                       │   │
│  │  │  + Embeddings    │     │       │  ┌──────────────────────────┐  │   │
│  │  └──────────────────┘     │       │  │  AI Employees            │  │   │
│  │          ▼                 │       │  │  - Unique personalities  │  │   │
│  │  ┌──────────────────┐     │       │  │  - Voice identities      │  │   │
│  │  │  6-Step Dialogue │     │       │  │  - CrewAI orchestration  │  │   │
│  │  │  Loop            │     │       │  └──────────────────────────┘  │   │
│  │  └──────────────────┘     │       │          ▼                       │   │
│  │                            │       │  ┌──────────────────────────┐  │   │
│  └────────────────────────────┘       │  │  Meeting Room            │  │   │
│                                        │  │  - Multi-agent collab    │  │   │
│  ┌───────────────────────────────────┐│  │  - Voice-enabled         │  │   │
│  │   SHARED INFRASTRUCTURE           ││  └──────────────────────────┘  │   │
│  ├───────────────────────────────────┤│                                 │   │
│  │                                   ││  ┌──────────────────────────┐  │   │
│  │  • Local LLM (Ollama/LM Studio)  ││  │  Dashboard & Monitoring   │  │   │
│  │  • MCP Server Integration        ││  │  - Agent activity         │  │   │
│  │  • Voice Pipeline (TTS/STT)      ││  │  - Task completion        │  │   │
│  │  • Browser Automation            ││  │  - Metrics & analytics    │  │   │
│  │  • Vector Database (ChromaDB)    ││  └──────────────────────────┘  │   │
│  │  • SQLite Databases              ││                                 │   │
│  └───────────────────────────────────┘└─────────────────────────────────┘   │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Features

### Core Capabilities

✅ **100% Open Source & Free**
✅ **Fully Local** - No cloud APIs required
✅ **GPU Accelerated** - RTX 3060+ recommended
✅ **Indian Language Support** - 21 languages, 69 voices
✅ **Learning System** - Improves over time through skillbook
✅ **Voice-Enabled** - Natural conversation with AI employees
✅ **Browser Automation** - Auto-setup deployments
✅ **Real-Time Dashboard** - Monitor all activities
✅ **MCP Integration** - Extensible tool ecosystem

### System 1: ACE Features

- **Intelligent requirement gathering** through clarifying questions
- **Multi-template support** (RTF, CRISPE, few-shot, chain-of-thought)
- **G-Eval validation** with 4 quality metrics
- **Semantic skill search** using embeddings
- **Version control** for prompts
- **Usage tracking** and success metrics

### System 2: Workspace Features

- **AI employees with unique identities** (name, personality, voice)
- **Department-based organization** with role hierarchy
- **Multi-agent collaboration** in meeting rooms
- **Voice conversations** with emotion support
- **Auto-deployment** to GitHub, Vercel, Railway
- **Health monitoring** of deployed products
- **AI-suggested improvements** for products

---

## 🚀 Quick Start

### Prerequisites

```bash
# Hardware
- 16GB+ RAM
- 8GB+ VRAM GPU (RTX 3060 or better)
- 50GB free disk space

# Software
- Python 3.11+
- CUDA 11.8+ (for GPU acceleration)
- Git
```

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd unified-ai-workspace

# 2. Install Ollama (recommended LLM provider)
curl -fsSL https://ollama.com/install.sh | sh

# 3. Pull required models
ollama pull qwen2.5:7b           # Primary model
ollama pull qwen2.5-coder:7b     # Code generation
ollama pull llama3.1:8b          # Alternative model

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Download TTS/STT models (optional but recommended for voice)
python scripts/download_voice_models.py

# 7. Initialize databases
python scripts/init_databases.py

# 8. Create configuration
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your preferences

# 9. Run setup verification
python scripts/verify_setup.py
```

### First Run

```bash
# Start the unified system
python main.py

# Or start individual systems:

# System 1 only (ACE Prompt Engineering)
python main.py --system ace

# System 2 only (AI Workspace)
python main.py --system workspace

# With dashboard
python main.py --dashboard

# With voice enabled
python main.py --voice
```

---

## 💡 Usage Examples

### Example 1: Generate Optimized Prompt (System 1)

```python
from system1_ace import ACEDialogue

# Initialize dialogue
ace = ACEDialogue()

# Interactive session
prompt = ace.generate_prompt_interactive()

# Or programmatic
result = ace.generate_prompt(
    task_type="creative_writing",
    domain="marketing",
    audience="technical_professionals",
    requirements=["concise", "data-driven", "actionable"]
)

print(result.final_prompt)
print(f"Quality score: {result.validation_score}")
```

### Example 2: Deploy AI Workforce (System 2)

```python
from system2_workspace import UnifiedWorkspace
from system2_workspace.departments import SalesDepartment

# Initialize workspace
workspace = UnifiedWorkspace()

# Create sales team
sales_dept = SalesDepartment()

# Assign task
result = await sales_dept.generate_outreach_campaign(
    target_audience="SaaS founders",
    product="AI development tools",
    channels=["email", "linkedin"]
)

print(result.campaign_strategy)
```

### Example 3: Voice-Enabled Meeting

```python
from system2_workspace import MeetingRoom

# Create meeting with AI employees
meeting = MeetingRoom(
    topic="Product roadmap for Q1 2025",
    participants=[
        "Priya Sharma (Sales Director)",
        "Rahul Verma (SDR)",
        "Anita Desai (R&D Lead)"
    ],
    voice_enabled=True
)

# Conduct meeting
async for audio_chunk in meeting.run_with_voice():
    # Stream audio output
    play_audio(audio_chunk)

# Get meeting summary
summary = meeting.get_summary()
print(summary.decisions)
print(summary.action_items)
```

### Example 4: Browser Automation for Deployment

```python
from browser import AgenticBrowserController

browser = AgenticBrowserController()

# Auto-setup GitHub repository
await browser.execute_task("""
Go to github.com, create new repository named 'ai-assistant',
initialize with README, add MIT license
""")

# Auto-deploy to Vercel
await browser.execute_task("""
Go to vercel.com, import GitHub repository 'ai-assistant',
configure build settings for Next.js, deploy
""")
```

### Example 5: Full Integration (Both Systems)

```python
from integration import UnifiedAIWorkspace

workspace = UnifiedAIWorkspace()

# R&D team uses ACE to improve the prompt engineering system
await workspace.improve_prompt_system()

# Deploy a project and have AI team monitor it
await workspace.deploy_and_monitor({
    "name": "customer-chatbot",
    "hosting": "vercel",
    "repository": "github.com/user/chatbot"
})

# Schedule recurring improvement meetings
workspace.schedule_improvement_cycle(
    product_id="customer-chatbot",
    frequency="weekly"
)
```

---

## 📁 Project Structure

```
unified-ai-workspace/
├── core/                          # Shared infrastructure
│   ├── config.py                  # Configuration management
│   ├── database.py                # SQLite + ChromaDB
│   └── llm_manager.py             # LLM provider abstraction
│
├── system1_ace/                   # ACE Prompt Engineering
│   ├── agents/                    # Multi-role agents
│   │   ├── analyzer.py
│   │   ├── generator.py
│   │   ├── validator.py
│   │   ├── reflector.py
│   │   └── skill_manager.py
│   ├── skillbook/                 # Skill storage
│   │   ├── database.py
│   │   └── embeddings.py
│   └── dialogue.py                # 6-step dialogue flow
│
├── system2_workspace/             # AI Workspace Dashboard
│   ├── departments/               # Department implementations
│   │   ├── sales.py
│   │   ├── marketing.py
│   │   ├── operations.py
│   │   ├── customer_success.py
│   │   ├── developers.py
│   │   └── rnd.py
│   ├── employees/                 # AI employee management
│   ├── meeting_room.py            # Multi-agent collaboration
│   └── dashboard.py               # Monitoring dashboard
│
├── voice/                         # Voice pipeline
│   ├── tts_engine.py              # Text-to-Speech
│   ├── stt_engine.py              # Speech-to-Text
│   └── voice_pipeline.py          # STT → LLM → TTS
│
├── browser/                       # Browser automation
│   └── controller.py              # Agentic browser control
│
├── integration/                   # System interconnection
│   ├── unified_workspace.py       # Main integration
│   └── mcp_server.py              # MCP tools
│
├── config/                        # Configuration files
│   ├── config.yaml                # Main config
│   ├── employees.yaml             # AI employee definitions
│   ├── departments.yaml           # Department structure
│   └── mcp_config.json            # MCP server config
│
├── scripts/                       # Utilities
│   ├── init_databases.py          # Database initialization
│   ├── download_voice_models.py   # Download TTS/STT models
│   └── verify_setup.py            # Setup verification
│
├── data/                          # Runtime data (gitignored)
│   ├── skillbook.db               # Skills database
│   ├── workspace.db               # Workspace database
│   └── vector_db/                 # Embeddings storage
│
├── main.py                        # Main entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🔧 Configuration

### Main Configuration (`config/config.yaml`)

```yaml
# LLM Configuration
llm:
  provider: "ollama"  # ollama, lm_studio, llama_cpp
  base_url: "http://localhost:11434"
  default_model: "qwen2.5:7b"
  function_calling_model: "qwen2.5:7b"
  code_model: "qwen2.5-coder:7b"
  temperature: 0.7
  max_tokens: 4096

# Voice Configuration
voice:
  enabled: true
  tts_engine: "indic_parler"  # indic_parler, indicf5, xtts, mms
  stt_engine: "indic_conformer"  # indic_conformer, whisper
  default_language: "hindi"
  default_voice_gender: "female"

# Browser Configuration
browser:
  enabled: true
  headless: false
  driver: "browser_use"  # browser_use, playwright, selenium

# Dashboard Configuration
dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 8501
  auto_refresh_interval: 5

# Database paths
database:
  skillbook_path: "./data/skillbook.db"
  workspace_path: "./data/workspace.db"
  vector_db_path: "./data/vector_db"
```

### AI Employees Configuration (`config/employees.yaml`)

```yaml
employees:
  - name: "Priya Sharma"
    employee_id: "emp_001"
    department: "sales"
    role: "Sales Director"
    personality:
      traits: ["strategic", "data-driven", "motivational"]
      communication_style: "formal"
    voice_config:
      engine: "indic_parler"
      gender: "female"
      language: "hindi"
      description: "professional female with clear articulation"
      default_emotion: "confident"
    llm_model: "llama3.1:8b"

  - name: "Rahul Verma"
    employee_id: "emp_002"
    department: "sales"
    role: "SDR Agent"
    personality:
      traits: ["energetic", "persistent", "friendly"]
      communication_style: "conversational"
    voice_config:
      engine: "indicf5_clone"
      reference_audio: "voices/rahul_sample.wav"
    llm_model: "qwen2.5:7b"
```

---

## 🎤 Voice Pipeline

### Supported TTS Engines

1. **AI4Bharat Indic Parler-TTS** (Primary)
   - 21 Indian languages
   - 69 voice variants
   - 10 emotions (command, anger, happy, sad, etc.)
   - 24kHz sample rate

2. **AI4Bharat IndicF5** (Voice Cloning)
   - 11 languages
   - Clone from 3-10 second reference audio
   - Cross-lingual synthesis

3. **Coqui XTTS-v2** (Fallback)
   - 17 languages
   - High-quality voice cloning
   - Zero-shot multilingual

4. **Meta MMS-TTS** (Wide Coverage)
   - 1,107 languages
   - Lower quality but widest support

### Supported STT Engines

1. **AI4Bharat IndicConformer** (Primary)
   - 22 Indian languages
   - Lowest WER for Indian accents
   - Two architectures: RNN-T and CTC

2. **AI4Bharat IndicWhisper** (Alternative)
   - Fine-tuned Whisper for Indian languages
   - Better than base Whisper for Hindi/Indian English

---

## 🌐 Browser Automation

### Supported Drivers

1. **browser-use** (Primary) - LLM-driven, natural language control
2. **Playwright** - Fast, modern automation
3. **Selenium** - Fallback, widest compatibility

### Common Automation Tasks

```python
# GitHub repository creation
browser.execute_task("Create new GitHub repo 'my-project' with MIT license")

# Vercel deployment
browser.execute_task("Deploy GitHub repo 'my-project' to Vercel")

# Railway setup
browser.execute_task("Create Railway project, add PostgreSQL database")

# Environment variable configuration
browser.execute_task("Add environment variables to Vercel project: API_KEY, DB_URL")
```

---

## 📊 Dashboard

The dashboard provides real-time monitoring of:

- **Agent Activity Feed** - Live view of all agent actions
- **Department Metrics** - Tasks completed, success rates, token usage
- **Deployed Products** - Health scores, uptime, performance
- **Meeting Summaries** - Decisions, action items, participants
- **Improvement Suggestions** - AI-generated product enhancements

Access at: `http://localhost:8501` (default)

---

## 🔌 MCP Integration

### Available MCP Tools

**System 1 (ACE):**
- `generate_prompt` - Generate optimized prompt
- `retrieve_skills` - Search skillbook
- `validate_prompt` - Quality assessment
- `store_skill` - Save new pattern

**System 2 (Workspace):**
- `assign_task` - Delegate to AI employee
- `create_meeting` - Schedule collaboration
- `deploy_product` - Auto-deploy to hosting
- `get_metrics` - Fetch department stats

**Shared:**
- `browser_execute` - Browser automation
- `voice_synthesize` - Generate speech
- `voice_transcribe` - Speech-to-text

### MCP Configuration

Edit `config/mcp_config.json`:

```json
{
  "mcpServers": {
    "unified_workspace": {
      "command": "python",
      "args": ["integration/mcp_server.py"],
      "env": {
        "CONFIG_PATH": "./config/config.yaml"
      }
    }
  }
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Test individual systems
pytest tests/test_ace.py
pytest tests/test_workspace.py

# Test with coverage
pytest --cov=. --cov-report=html

# Integration tests
pytest tests/test_integration.py -v
```

---

## 🛠️ Development

### Adding New AI Employee

```yaml
# Add to config/employees.yaml
- name: "Your Employee"
  employee_id: "emp_xxx"
  department: "your_department"
  role: "Your Role"
  personality:
    traits: ["trait1", "trait2"]
  voice_config:
    engine: "indic_parler"
    gender: "female"
  llm_model: "qwen2.5:7b"
```

### Adding New Department

```python
# Create system2_workspace/departments/your_dept.py
from crewai import Agent, Crew, Task
from ..employees import create_employee

class YourDepartment:
    def __init__(self):
        self.agents = []
        self._init_agents()

    def _init_agents(self):
        # Define agents for this department
        pass

    def your_crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=[...],
            process=Process.sequential
        )
```

### Adding New Skill to Skillbook

```python
from system1_ace import Skillbook

skillbook = Skillbook()

skillbook.add_skill(
    skill_name="creative_storytelling",
    prompt_template="You are a creative storyteller...",
    skill_type="template",
    description="Template for creative story generation",
    tags=["creative", "storytelling", "narrative"]
)
```

---

## 📈 Performance Optimization

### GPU Acceleration

```bash
# Install GPU-optimized PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Model Quantization

```bash
# Pull quantized models (faster inference, lower VRAM)
ollama pull qwen2.5:7b-q4_K_M      # 4-bit quantized
ollama pull qwen2.5:7b-q5_K_M      # 5-bit (better quality)
```

### Database Optimization

```python
# Enable WAL mode for better concurrency
sqlite3 data/skillbook.db "PRAGMA journal_mode=WAL;"
sqlite3 data/workspace.db "PRAGMA journal_mode=WAL;"
```

---

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama service
systemctl restart ollama  # Linux
# Or restart Ollama app manually (Mac/Windows)
```

### Voice Model Loading Errors

```bash
# Re-download models
python scripts/download_voice_models.py --force

# Check model cache
ls ~/.cache/huggingface/hub/
```

### Database Lock Errors

```bash
# Close all connections and rebuild
python scripts/rebuild_databases.py
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas for improvement:
- Additional language support
- More TTS/STT engines
- New department types
- Enhanced browser automation
- Performance optimizations

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built using open-source projects:
- **Ollama** - Local LLM serving
- **CrewAI** - Multi-agent framework
- **LangChain** - LLM orchestration
- **AI4Bharat** - Indic language models
- **browser-use** - LLM-driven browser automation
- **ChromaDB** - Vector database
- **Streamlit** - Dashboard UI

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@your-domain.com

---

## 🗺️ Roadmap

### Q1 2025
- [ ] Complete all department implementations
- [ ] Advanced voice emotion control
- [ ] Multi-modal embeddings (text + images)
- [ ] Distributed deployment support

### Q2 2025
- [ ] Web UI for both systems
- [ ] Mobile app integration
- [ ] Cloud deployment option (optional)
- [ ] Enterprise features (SSO, audit logs)

### Q3 2025
- [ ] Video generation capabilities
- [ ] Advanced browser automation (RPA)
- [ ] Auto-scaling for multiple projects
- [ ] Blockchain integration for audit trails

---

**Built with ❤️ for the AI community**
