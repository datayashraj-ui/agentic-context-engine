#!/usr/bin/env python3
"""
Unified AI Workspace - Main Entry Point

Launches the complete AI system or individual components based on arguments.

Usage:
    python main.py                    # Start full system
    python main.py --system ace       # ACE Prompt Engineering only
    python main.py --system workspace # AI Workspace Dashboard only
    python main.py --dashboard       # With web dashboard
    python main.py --voice           # With voice enabled
    python main.py --no-browser      # Disable browser automation
"""

import argparse
import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import load_config, get_database, get_llm
from core.config import Config

console = Console()


def print_banner():
    """Print startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  🚀 UNIFIED AI WORKSPACE v2.0                              ║
║                                                                            ║
║   System 1: ACE Prompt Engineering Architect                              ║
║   System 2: Universal AI Workspace Dashboard                              ║
║                                                                            ║
║   100% Open Source | Fully Local | GPU Accelerated                       ║
║                                                                            ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def verify_dependencies(config: Config):
    """Verify required dependencies and models"""
    console.print("\n[bold yellow]Verifying dependencies...[/bold yellow]")

    issues = []

    # Check LLM provider
    try:
        llm = get_llm()
        models = llm.list_models()
        console.print(f"✓ LLM provider ({config.llm.provider}) connected", style="green")
        console.print(f"  Available models: {', '.join(models[:3])}...", style="dim")

        # Check for required models
        if config.llm.default_model not in models:
            issues.append(f"Model '{config.llm.default_model}' not found. Run: ollama pull {config.llm.default_model}")
    except Exception as e:
        issues.append(f"LLM provider error: {e}")
        console.print(f"✗ LLM provider error: {e}", style="red")

    # Check databases
    try:
        db = get_database()
        console.print("✓ Databases initialized", style="green")
    except Exception as e:
        issues.append(f"Database error: {e}")
        console.print(f"✗ Database error: {e}", style="red")

    # Check voice models (if enabled)
    if config.voice.enabled:
        try:
            from transformers import AutoModel
            # Test loading a model (minimal check)
            console.print("✓ Voice pipeline dependencies available", style="green")
        except ImportError:
            issues.append("Voice dependencies not installed. Run: pip install transformers torch torchaudio")
            console.print("✗ Voice dependencies missing", style="red")

    # Check browser automation (if enabled)
    if config.browser.enabled:
        try:
            import playwright
            console.print("✓ Browser automation available", style="green")
        except ImportError:
            issues.append("Browser automation not installed. Run: pip install playwright && playwright install")
            console.print("✗ Browser automation missing", style="red")

    if issues:
        console.print("\n[bold red]⚠ Setup incomplete:[/bold red]")
        for issue in issues:
            console.print(f"  • {issue}", style="yellow")
        console.print("\nRun setup with: python scripts/verify_setup.py")
        return False

    console.print("\n[bold green]✓ All dependencies verified[/bold green]\n")
    return True


async def start_ace_system(config: Config):
    """Start System 1: ACE Prompt Engineering"""
    console.print("\n[bold cyan]Starting ACE Prompt Engineering Architect...[/bold cyan]\n")

    try:
        from system1_ace import ACEDialogue

        ace = ACEDialogue()

        console.print("[bold green]ACE System Ready![/bold green]")
        console.print("\nYou can now:")
        console.print("  1. Generate prompts interactively")
        console.print("  2. Search skillbook for patterns")
        console.print("  3. Validate existing prompts")
        console.print("  4. Learn from feedback\n")

        # Interactive mode
        while True:
            console.print("\n[bold]What would you like to do?[/bold]")
            console.print("  1. Generate new prompt")
            console.print("  2. Search skillbook")
            console.print("  3. Validate prompt")
            console.print("  4. View metrics")
            console.print("  5. Exit")

            choice = console.input("\n[bold cyan]Choice (1-5):[/bold cyan] ")

            if choice == "1":
                result = await ace.generate_prompt_interactive()
                console.print("\n[bold green]Generated Prompt:[/bold green]")
                console.print(Panel(result.final_prompt, title="Optimized Prompt"))
                console.print(f"\nQuality Score: {result.validation_score:.2f}/5.0")

            elif choice == "2":
                query = console.input("\n[bold cyan]Search query:[/bold cyan] ")
                skills = ace.search_skills(query, limit=5)
                console.print(f"\nFound {len(skills)} matching skills:")
                for skill in skills:
                    console.print(f"  • {skill.skill_name} ({skill.skill_type}) - {skill.success_rate:.0%} success")

            elif choice == "3":
                prompt = console.input("\n[bold cyan]Enter prompt to validate:[/bold cyan] ")
                validation = await ace.validate_prompt(prompt)
                console.print("\n[bold green]Validation Results:[/bold green]")
                table = Table(show_header=True)
                table.add_column("Metric")
                table.add_column("Score")
                table.add_row("Clarity", f"{validation.clarity_score:.1f}/5")
                table.add_row("Completeness", f"{validation.completeness_score:.1f}/5")
                table.add_row("Specificity", f"{validation.specificity_score:.1f}/5")
                table.add_row("Coherence", f"{validation.coherence_score:.1f}/5")
                console.print(table)

            elif choice == "4":
                metrics = ace.get_metrics()
                console.print("\n[bold green]ACE Metrics:[/bold green]")
                console.print(f"  Total skills: {metrics['total_skills']}")
                console.print(f"  Sessions completed: {metrics['sessions_completed']}")
                console.print(f"  Avg success rate: {metrics['avg_success_rate']:.1%}")

            elif choice == "5":
                break

    except Exception as e:
        console.print(f"\n[bold red]Error starting ACE system: {e}[/bold red]")
        import traceback
        traceback.print_exc()


async def start_workspace_system(config: Config):
    """Start System 2: AI Workspace Dashboard"""
    console.print("\n[bold cyan]Starting AI Workspace Dashboard...[/bold cyan]\n")

    try:
        from system2_workspace import UnifiedWorkspace

        workspace = UnifiedWorkspace()

        console.print("[bold green]Workspace System Ready![/bold green]")
        console.print("\nAvailable departments:")
        console.print("  • Sales (2 AI employees)")
        console.print("  • Marketing (3 AI employees)")
        console.print("  • Operations (2 AI employees)")
        console.print("  • Customer Success (2 AI employees)")
        console.print("  • Developers (3 AI employees)")
        console.print("  • R&D (2 AI employees)\n")

        # Interactive mode
        while True:
            console.print("\n[bold]What would you like to do?[/bold]")
            console.print("  1. Assign task to department")
            console.print("  2. Create meeting")
            console.print("  3. Deploy product")
            console.print("  4. View dashboard")
            console.print("  5. Exit")

            choice = console.input("\n[bold cyan]Choice (1-5):[/bold cyan] ")

            if choice == "1":
                dept = console.input("Department (sales/marketing/ops/cs/dev/rnd): ")
                task = console.input("Task description: ")
                result = await workspace.assign_task(dept, task)
                console.print(f"\n[bold green]Task completed:[/bold green]\n{result}")

            elif choice == "2":
                topic = console.input("Meeting topic: ")
                participants = console.input("Participants (comma-separated): ").split(',')
                result = await workspace.create_meeting(topic, [p.strip() for p in participants])
                console.print(f"\n[bold green]Meeting summary:[/bold green]")
                console.print(Panel(result.summary))

            elif choice == "3":
                name = console.input("Product name: ")
                repo = console.input("GitHub repo URL: ")
                hosting = console.input("Hosting (vercel/railway/render): ")
                result = await workspace.deploy_product(name, repo, hosting)
                console.print(f"\n[bold green]Deployment:[/bold green] {result.status}")
                console.print(f"URL: {result.url}")

            elif choice == "4":
                await workspace.show_dashboard()

            elif choice == "5":
                break

    except Exception as e:
        console.print(f"\n[bold red]Error starting Workspace system: {e}[/bold red]")
        import traceback
        traceback.print_exc()


async def start_unified_system(config: Config):
    """Start both systems integrated"""
    console.print("\n[bold cyan]Starting Unified AI Workspace...[/bold cyan]\n")

    try:
        from integration import UnifiedAIWorkspace

        workspace = UnifiedAIWorkspace()

        console.print("[bold green]Unified System Ready![/bold green]\n")

        # Main menu
        while True:
            console.print("\n[bold]Unified AI Workspace[/bold]")
            console.print("  1. ACE Prompt Engineering")
            console.print("  2. AI Workforce Management")
            console.print("  3. Deploy & Monitor Product")
            console.print("  4. Schedule Improvement Meeting")
            console.print("  5. View Overall Metrics")
            console.print("  6. Exit")

            choice = console.input("\n[bold cyan]Choice (1-6):[/bold cyan] ")

            if choice == "1":
                await start_ace_system(config)
            elif choice == "2":
                await start_workspace_system(config)
            elif choice == "3":
                name = console.input("Product name: ")
                repo = console.input("GitHub repo: ")
                hosting = console.input("Hosting: ")
                await workspace.deploy_and_monitor({
                    "name": name,
                    "repository": repo,
                    "hosting": hosting
                })
            elif choice == "4":
                product_id = console.input("Product ID: ")
                await workspace.conduct_meeting(
                    topic=f"Improvement review for {product_id}",
                    participants=["R&D Lead", "Dev Lead", "Product Manager"]
                )
            elif choice == "5":
                metrics = await workspace.get_overall_metrics()
                console.print("\n[bold green]Overall Metrics:[/bold green]")
                console.print(f"  Active employees: {metrics['active_employees']}")
                console.print(f"  Tasks completed today: {metrics['tasks_today']}")
                console.print(f"  Deployed products: {metrics['deployed_products']}")
                console.print(f"  System uptime: {metrics['uptime']}")
            elif choice == "6":
                break

    except Exception as e:
        console.print(f"\n[bold red]Error starting Unified system: {e}[/bold red]")
        import traceback
        traceback.print_exc()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Unified AI Workspace - ACE + AI Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--system",
        choices=["ace", "workspace", "unified"],
        default="unified",
        help="Which system to start (default: unified)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="./config/config.yaml",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Launch web dashboard (Streamlit)"
    )

    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable voice pipeline"
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Disable browser automation"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_args()

    # Print banner
    print_banner()

    # Load configuration
    try:
        if Path(args.config).exists():
            config = load_config(args.config)
        else:
            console.print(f"[yellow]Config file not found: {args.config}[/yellow]")
            console.print("Using default configuration from environment variables")
            config = load_config()

        # Override with CLI args
        if args.voice:
            config.voice.enabled = True
        if args.no_browser:
            config.browser.enabled = False
        if args.debug:
            config.debug = True

    except Exception as e:
        console.print(f"[bold red]Configuration error: {e}[/bold red]")
        return 1

    # Verify dependencies
    if not verify_dependencies(config):
        console.print("\n[bold yellow]You can continue anyway, but some features may not work.[/bold yellow]")
        if not console.input("Continue? (y/n): ").lower().startswith('y'):
            return 1

    # Start requested system
    try:
        if args.system == "ace":
            await start_ace_system(config)
        elif args.system == "workspace":
            await start_workspace_system(config)
        else:
            await start_unified_system(config)

    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]Shutting down gracefully...[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1

    console.print("\n[bold green]Goodbye! 👋[/bold green]\n")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
