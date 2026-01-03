#!/usr/bin/env python3
"""
Initialize databases for Unified AI Workspace

Creates and initializes:
- Skillbook database (skills, sessions, validations)
- Workspace database (employees, runs, products, meetings)
- Vector database (ChromaDB for embeddings)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import load_config, get_database
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def init_databases():
    """Initialize all databases"""
    console.print("\n[bold cyan]Initializing Unified AI Workspace Databases[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Load configuration
        task = progress.add_task("Loading configuration...", total=None)
        config = load_config()
        progress.update(task, completed=True)
        console.print("✓ Configuration loaded", style="green")

        # Ensure directories exist
        task = progress.add_task("Creating directories...", total=None)
        config.ensure_directories()
        progress.update(task, completed=True)
        console.print("✓ Directories created", style="green")

        # Initialize databases
        task = progress.add_task("Initializing SQLite databases...", total=None)
        db = get_database()
        db.init_all_schemas()
        progress.update(task, completed=True)
        console.print("✓ SQLite databases initialized", style="green")
        console.print(f"  • Skillbook: {config.database.skillbook_path}", style="dim")
        console.print(f"  • Workspace: {config.database.workspace_path}", style="dim")

        # Initialize vector database
        task = progress.add_task("Initializing vector database...", total=None)
        if db.vector_db:
            # Create collections
            db.vector_db.get_or_create_collection("skills")
            progress.update(task, completed=True)
            console.print("✓ Vector database initialized", style="green")
            console.print(f"  • ChromaDB: {config.database.vector_db_path}", style="dim")
        else:
            progress.update(task, completed=True)
            console.print("⚠ ChromaDB not available (semantic search disabled)", style="yellow")

        # Seed initial data (optional)
        task = progress.add_task("Seeding initial data...", total=None)
        seed_initial_data(db)
        progress.update(task, completed=True)
        console.print("✓ Initial data seeded", style="green")

    console.print("\n[bold green]✓ Database initialization complete![/bold green]\n")


def seed_initial_data(db):
    """Seed databases with initial data"""
    from system1_ace.skillbook import Skillbook

    skillbook = Skillbook()

    # Add initial prompt engineering skills
    initial_skills = [
        {
            "skill_name": "rtf_template",
            "skill_type": "template",
            "description": "Role-Task-Format template for structured prompts",
            "prompt_template": """You are a [ROLE].

Your task is to [TASK].

Format your response as:
[FORMAT]
""",
            "tags": ["template", "rtf", "basic"],
            "metadata": {"version": "1.0", "success_examples": 0}
        },
        {
            "skill_name": "crispe_template",
            "skill_type": "template",
            "description": "CRISPE framework (Capacity, Role, Insight, Statement, Personality, Experiment)",
            "prompt_template": """# Capacity and Role
You are an expert [ROLE] with deep knowledge in [DOMAIN].

# Insight
[BACKGROUND CONTEXT AND INSIGHT]

# Statement
[CLEAR TASK STATEMENT]

# Personality
[DESIRED TONE AND STYLE]

# Experiment
[EXPECTED OUTPUT FORMAT AND CONSTRAINTS]
""",
            "tags": ["template", "crispe", "advanced"],
            "metadata": {"version": "1.0"}
        },
        {
            "skill_name": "few_shot_pattern",
            "skill_type": "pattern",
            "description": "Few-shot learning pattern with examples",
            "prompt_template": """Given the following examples:

Example 1:
Input: [INPUT_1]
Output: [OUTPUT_1]

Example 2:
Input: [INPUT_2]
Output: [OUTPUT_2]

Now, for the following input:
Input: [NEW_INPUT]
Output:
""",
            "tags": ["pattern", "few-shot", "examples"],
            "metadata": {"version": "1.0"}
        },
        {
            "skill_name": "chain_of_thought",
            "skill_type": "technique",
            "description": "Chain-of-thought reasoning technique",
            "prompt_template": """Let's approach this step-by-step:

1. First, let's understand what we're being asked: [RESTATE PROBLEM]
2. Let's identify the key components: [LIST KEY ELEMENTS]
3. Now, let's reason through this: [LOGICAL STEPS]
4. Based on this reasoning: [CONCLUSION]
""",
            "tags": ["technique", "reasoning", "step-by-step"],
            "metadata": {"version": "1.0"}
        },
        {
            "skill_name": "creative_writing_domain",
            "skill_type": "domain",
            "description": "Domain-specific patterns for creative writing",
            "prompt_template": """As a creative writer, craft content that:
- Engages the reader from the first sentence
- Uses vivid, sensory details
- Maintains consistent voice and tone
- Builds narrative momentum
- Ends with impact

Topic: [TOPIC]
Style: [STYLE]
Length: [LENGTH]
""",
            "tags": ["domain", "creative", "writing"],
            "metadata": {"version": "1.0"}
        }
    ]

    for skill in initial_skills:
        try:
            skillbook.add_skill(**skill)
            console.print(f"  • Added skill: {skill['skill_name']}", style="dim green")
        except Exception as e:
            console.print(f"  ⚠ Failed to add {skill['skill_name']}: {e}", style="yellow")

    # Seed AI employees
    conn = db.connect_workspace()

    employees = [
        {
            "employee_id": "emp_001",
            "name": "Priya Sharma",
            "department": "sales",
            "role": "Sales Director",
            "personality": "Strategic, data-driven, motivational",
            "voice_config": '{"engine": "indic_parler", "gender": "female", "language": "hindi"}',
            "llm_model": "llama3.1:8b"
        },
        {
            "employee_id": "emp_002",
            "name": "Rahul Verma",
            "department": "sales",
            "role": "SDR Agent",
            "personality": "Energetic, persistent, friendly",
            "voice_config": '{"engine": "indic_parler", "gender": "male", "language": "hindi"}',
            "llm_model": "qwen2.5:7b"
        },
        {
            "employee_id": "emp_003",
            "name": "Anita Desai",
            "department": "rnd",
            "role": "R&D Lead",
            "personality": "Analytical, innovative, detail-oriented",
            "voice_config": '{"engine": "indic_parler", "gender": "female", "language": "english"}',
            "llm_model": "qwen2.5:7b"
        }
    ]

    for emp in employees:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO employees
                (employee_id, name, department, role, personality, voice_config, llm_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                emp["employee_id"],
                emp["name"],
                emp["department"],
                emp["role"],
                emp["personality"],
                emp["voice_config"],
                emp["llm_model"]
            ))
            console.print(f"  • Added employee: {emp['name']} ({emp['department']})", style="dim green")
        except Exception as e:
            console.print(f"  ⚠ Failed to add employee {emp['name']}: {e}", style="yellow")

    conn.commit()


if __name__ == "__main__":
    try:
        init_databases()
    except Exception as e:
        console.print(f"\n[bold red]Error during initialization: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
