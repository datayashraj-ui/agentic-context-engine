# Implementation Guide
## Completing the Unified AI Workspace

This guide explains how to complete the remaining components of the Unified AI Workspace.

---

## ✅ What's Already Built

The foundation is complete and functional:

### Core Infrastructure (100% Complete)
- ✅ **Configuration system** (`core/config.py`) - Full YAML + env variable support
- ✅ **Database layer** (`core/database.py`) - SQLite + ChromaDB integration
- ✅ **LLM manager** (`core/llm_manager.py`) - Ollama/LM Studio/llama.cpp support
- ✅ **Main entry point** (`main.py`) - CLI with interactive menus
- ✅ **Setup scripts** (`scripts/init_databases.py`) - Database initialization with seed data

### System 1: ACE Prompt Engineering (Foundation Complete)
- ✅ **Skillbook database** (`system1_ace/skillbook/database.py`) - Full CRUD with metrics
- ✅ **Embedding manager** (`system1_ace/skillbook/embeddings.py`) - Semantic search
- ⏳ **Agents** - Need implementation (templates below)
- ⏳ **Dialogue system** - Need implementation (template below)

### Documentation (100% Complete)
- ✅ **Comprehensive README** with architecture diagrams
- ✅ **Configuration examples** with detailed comments
- ✅ **This implementation guide**

---

## 🔨 What Needs Implementation

### 1. System 1 Agents (Priority: High)

Create the 5 agents in `system1_ace/agents/`:

#### Template for each agent:

```python
# system1_ace/agents/analyzer.py
from core import get_llm
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RequirementSpec:
    """Parsed requirement specification"""
    task_type: str
    domain: str
    audience: str
    requirements: list
    constraints: list
    format: str

class AnalyzerAgent:
    """Analyzes user requirements and extracts intent"""

    SYSTEM_PROMPT = """You analyze prompt requests to extract:
    - Task type (creative_writing, technical_docs, code_review, etc.)
    - Domain (marketing, engineering, research, etc.)
    - Target audience
    - Key requirements and constraints
    - Desired output format

    Return structured JSON with these fields."""

    def __init__(self):
        self.llm = get_llm()

    def analyze(self, user_request: str) -> RequirementSpec:
        """Parse user request into structured requirements"""
        prompt = f"{self.SYSTEM_PROMPT}\n\nUser request: {user_request}"

        response = self.llm.complete(
            prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3
        )

        # Parse JSON response
        import json
        data = json.loads(response)

        return RequirementSpec(**data)
```

**Similar pattern for:**
- `generator.py` - Uses skillbook + templates to generate prompts
- `validator.py` - G-Eval scoring (4 metrics)
- `reflector.py` - Analyzes validation results, suggests improvements
- `skill_manager.py` - Retrieves/stores skills from/to skillbook

### 2. Dialogue System (Priority: High)

```python
# system1_ace/dialogue.py
from .agents import (AnalyzerAgent, GeneratorAgent, ValidatorAgent,
                     ReflectorAgent, SkillManagerAgent)
from .skillbook import Skillbook

class ACEDialogue:
    """6-step interactive dialogue for prompt generation"""

    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.generator = GeneratorAgent()
        self.validator = ValidatorAgent()
        self.reflector = ReflectorAgent()
        self.skill_manager = SkillManagerAgent()
        self.skillbook = Skillbook()

    async def generate_prompt_interactive(self):
        """Interactive 6-step flow"""

        # Step 1: Gather requirements
        user_request = input("What type of prompt do you need? ")

        # Step 2: Analyze and confirm
        spec = self.analyzer.analyze(user_request)
        print(f"Understood: {spec}")
        confirmed = input("Is this correct? (y/n) ")

        if confirmed != 'y':
            # Re-gather requirements
            pass

        # Step 3: Generate prompt
        relevant_skills = self.skillbook.search_skills(
            query=f"{spec.task_type} {spec.domain}",
            limit=5
        )
        prompt_draft = self.generator.generate(spec, relevant_skills)

        # Step 4: Validate
        validation = self.validator.validate(prompt_draft)

        # Step 5: Refine if needed
        if validation.overall_score < 4.0:
            improvements = self.reflector.reflect(validation)
            prompt_draft = self.generator.refine(prompt_draft, improvements)

        # Step 6: Learn from feedback
        rating = int(input("Rate effectiveness (1-5): "))
        if rating >= 4:
            # Extract patterns and store
            self.skill_manager.learn_from_success(spec, prompt_draft)

        return prompt_draft
```

### 3. System 2: AI Workspace (Priority: Medium)

Create department implementations in `system2_workspace/departments/`:

#### Template:

```python
# system2_workspace/departments/sales.py
from crewai import Agent, Crew, Task, Process
from core import get_llm

class SalesDepartment:
    def __init__(self):
        self.llm = get_llm().get_langchain_llm()
        self._init_agents()

    def _init_agents(self):
        self.director = Agent(
            role="Sales Director",
            goal="Drive revenue growth through strategic sales initiatives",
            backstory="Experienced sales leader with data-driven approach",
            llm=self.llm,
            verbose=True
        )

        self.sdr = Agent(
            role="SDR Agent",
            goal="Generate qualified leads through outreach",
            backstory="Energetic and persistent sales development rep",
            llm=self.llm,
            verbose=True
        )

    def generate_outreach_campaign(self, target_audience, product, channels):
        """Generate sales outreach campaign"""
        task = Task(
            description=f"""
            Create outreach campaign for {product} targeting {target_audience}.
            Channels: {channels}
            Include: messaging strategy, email templates, LinkedIn scripts.
            """,
            expected_output="Complete campaign strategy with templates",
            agent=self.director
        )

        crew = Crew(
            agents=[self.director, self.sdr],
            tasks=[task],
            process=Process.sequential
        )

        return crew.kickoff()
```

**Repeat for:**
- `marketing.py` - Content creation, SEO, campaigns
- `operations.py` - Workflow automation, process optimization
- `customer_success.py` - Support, onboarding, health monitoring
- `developers.py` - Code generation, review, deployment
- `rnd.py` - Research, prototyping, innovation

### 4. Voice Pipeline (Priority: Medium)

```python
# voice/tts_engine.py
from transformers import AutoModel
import torch

class IndicTTSEngine:
    def __init__(self):
        self.model = AutoModel.from_pretrained(
            "ai4bharat/indic-parler-tts",
            trust_remote_code=True
        )

    def synthesize(self, text, language="hindi", emotion="neutral", voice_desc="professional female"):
        """Generate speech from text"""
        description = f"{voice_desc} speaker delivers {emotion} speech in {language}"

        # Generate audio
        audio = self.model.generate(text, description)
        return audio

# voice/stt_engine.py
from transformers import AutoModel

class IndicSTTEngine:
    def __init__(self):
        self.model = AutoModel.from_pretrained(
            "ai4bharat/indic-conformer-600m-multilingual",
            trust_remote_code=True
        )

    def transcribe(self, audio_path, language="hindi"):
        """Transcribe speech to text"""
        return self.model.transcribe(audio_path, language)

# voice/voice_pipeline.py
class VoiceAgentPipeline:
    """Complete STT → LLM → TTS pipeline"""

    def __init__(self):
        self.stt = IndicSTTEngine()
        self.tts = IndicTTSEngine()
        self.llm = get_llm()

    async def process_turn(self, audio_input):
        # 1. Transcribe
        text = self.stt.transcribe(audio_input)

        # 2. Generate response
        response = self.llm.complete(text)

        # 3. Synthesize
        audio = self.tts.synthesize(response)

        return audio
```

### 5. Browser Automation (Priority: Low - Optional)

```python
# browser/controller.py
from browser_use import Agent, Browser

class AgenticBrowserController:
    def __init__(self):
        self.browser = Browser()
        self.llm = get_llm().get_langchain_llm()

    async def execute_task(self, task_description):
        """Execute browser task using natural language"""
        agent = Agent(
            task=task_description,
            llm=self.llm,
            browser=self.browser
        )

        result = await agent.run()
        return result.final_result()
```

### 6. Integration Layer (Priority: Medium)

```python
# integration/unified_workspace.py
from system1_ace import ACEDialogue
from system2_workspace.departments import *

class UnifiedAIWorkspace:
    """Connects both systems"""

    def __init__(self):
        # System 1
        self.ace = ACEDialogue()

        # System 2
        self.departments = {
            "sales": SalesDepartment(),
            "marketing": MarketingDepartment(),
            # ...
        }

    async def improve_prompt_system(self):
        """R&D department analyzes and improves ACE"""
        rnd = self.departments["rnd"]

        # Analyze skillbook
        skills = self.ace.skillbook.get_top_skills()

        # Get improvement suggestions
        improvements = await rnd.analyze_system(skills)

        # Apply improvements
        for improvement in improvements:
            self.ace.skillbook.add_skill(**improvement)
```

### 7. Dashboard UI (Priority: Low - Optional)

```python
# system2_workspace/dashboard.py
import streamlit as st
from core.database import get_database

def show_dashboard():
    """Streamlit dashboard"""
    st.title("🤖 Unified AI Workspace Dashboard")

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Active Employees", "14")
    with col2:
        st.metric("Tasks Today", "42")
    with col3:
        st.metric("Deployed Products", "7")

    # Department activity
    st.subheader("Department Activity")

    db = get_database()
    conn = db.connect_workspace()

    # Fetch recent runs
    cursor = conn.execute("""
        SELECT department, COUNT(*) as tasks
        FROM agent_runs
        WHERE date(start_time) = date('now')
        GROUP BY department
    """)

    # Display chart
    data = cursor.fetchall()
    st.bar_chart({row[0]: row[1] for row in data})
```

---

## 🚀 Quick Implementation Order

### Phase 1: Core Functionality (Week 1)
1. ✅ Core infrastructure - **DONE**
2. ✅ Skillbook system - **DONE**
3. **System 1 Agents** - Implement all 5 agents
4. **Dialogue system** - Connect agents into flow

### Phase 2: AI Workforce (Week 2)
5. **Department templates** - Create 2-3 departments (Sales, R&D, Developers)
6. **Meeting room** - Multi-agent collaboration
7. **Integration layer** - Connect System 1 + 2

### Phase 3: Advanced Features (Week 3+)
8. **Voice pipeline** - TTS/STT integration
9. **Browser automation** - Deployment tasks
10. **Dashboard UI** - Streamlit interface

---

## 💡 Development Tips

### Testing Individual Components

```bash
# Test skillbook
python -c "from system1_ace.skillbook import Skillbook; s = Skillbook(); print(s.get_top_skills())"

# Test LLM manager
python -c "from core import get_llm; llm = get_llm(); print(llm.complete('Hello!'))"

# Test database
python scripts/init_databases.py
sqlite3 data/skillbook.db "SELECT * FROM skills;"
```

### Using Without Voice/Browser

If you want to skip voice and browser features:

```yaml
# config/config.yaml
voice:
  enabled: false

browser:
  enabled: false
```

The system will work fine - just without those features.

### Incremental Development

You can run the system even with incomplete components:

1. **Just ACE (no agents)**: Use skillbook directly
2. **Just Workspace (no departments)**: Create simple task executor
3. **No voice/browser**: Core LLM features still work

---

## 📚 Reference Implementation

Check the existing ACE framework in the parent directory:
- `../ace/` - Reference for agent patterns
- `../ace/roles.py` - Agent, Reflector, SkillManager examples
- `../examples/` - Usage examples

---

## 🎯 Minimum Viable Product (MVP)

To get a working MVP quickly, implement:

**Must Have:**
1. ✅ Core infrastructure - DONE
2. ✅ Skillbook - DONE
3. **Analyzer + Generator agents** - 2 agents minimum
4. **Simple dialogue flow** - Basic Q&A loop

**Skip for MVP:**
- Voice pipeline
- Browser automation
- Dashboard UI
- Meeting room

This gives you a functional prompt engineering system in ~200 lines of code.

---

## 🤝 Need Help?

Stuck on implementation? Check:
1. This guide's templates above
2. The comprehensive README
3. Configuration examples
4. Parent ACE framework for patterns

Happy coding! 🚀
