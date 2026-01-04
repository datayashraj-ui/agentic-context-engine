#!/usr/bin/env python3
"""
GitHub Repo Product Converter CLI

Convert GitHub repositories into fully functional products using ACE.

Usage:
    python scripts/repo_converter_cli.py <repo_url> [options]

Examples:
    # Convert a single repo
    python scripts/repo_converter_cli.py https://github.com/user/repo

    # Convert with custom output directory
    python scripts/repo_converter_cli.py https://github.com/user/repo --output ./my_project

    # Batch convert multiple repos
    python scripts/repo_converter_cli.py --batch repos.txt

    # Use specific LLM model
    python scripts/repo_converter_cli.py https://github.com/user/repo --model gpt-4
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ace.llm_providers.litellm_client import LiteLLMClient
from ace.integrations.github_repo_converter import GitHubRepoConverter, ConversionResult
from ace.skillbook import Skillbook

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert GitHub repos into working products using ACE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/user/broken-project
  %(prog)s https://github.com/user/repo --output ./fixed_repo
  %(prog)s --batch repo_list.txt --model gpt-4
  %(prog)s https://github.com/user/repo --no-learning --verbose
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "repo_url",
        nargs="?",
        help="GitHub repository URL to convert"
    )
    input_group.add_argument(
        "--batch",
        type=str,
        help="File containing list of repo URLs (one per line)"
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output directory for converted repo (default: ./converted_repos/<repo_name>)"
    )

    # LLM options
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.1,
        help="LLM temperature (default: 0.1)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for the LLM provider (or set via environment variable)"
    )

    # Skillbook options
    parser.add_argument(
        "--skillbook",
        type=str,
        default="repo_converter_skillbook.json",
        help="Path to skillbook file (default: repo_converter_skillbook.json)"
    )
    parser.add_argument(
        "--no-learning",
        action="store_true",
        help="Disable learning mode (don't update skillbook)"
    )

    # Other options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--save-skillbook-per-repo",
        action="store_true",
        help="Save skillbook to each converted repo directory"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    return parser.parse_args()


def load_repo_urls_from_file(file_path: str) -> List[str]:
    """Load repository URLs from a text file"""
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return urls


def print_conversion_summary(result: ConversionResult, verbose: bool = False):
    """Print a summary of the conversion results"""
    print("\n" + "="*70)
    print(f"Conversion Summary: {result.repo_url}")
    print("="*70)

    # Status with emoji
    status_emoji = {
        "success": "✅",
        "partial": "⚠️",
        "failed": "❌"
    }
    emoji = status_emoji.get(result.final_status, "❓")

    print(f"\n{emoji} Status: {result.final_status.upper()}")
    print(f"\n📊 Statistics:")
    print(f"  - Issues found: {len(result.original_issues)}")
    print(f"  - Fixes attempted: {len(result.fixes_attempted)}")
    print(f"  - Successful fixes: {len([f for f in result.fixes_attempted if f.success])}")
    print(f"  - Build successful: {'✅' if result.build_successful else '❌'}")

    if verbose and result.fixes_attempted:
        print(f"\n🔧 Fix Details:")
        for i, fix in enumerate(result.fixes_attempted, 1):
            status = "✅" if fix.success else "❌"
            print(f"\n  {i}. {status} {fix.issue.category} ({fix.issue.severity})")
            print(f"     Issue: {fix.issue.description}")
            print(f"     Fix: {fix.fix_applied}")
            if not fix.success and fix.error_message:
                print(f"     Error: {fix.error_message}")

    if result.skillbook_path:
        print(f"\n📚 Skillbook: {result.skillbook_path}")

    print("="*70)


def convert_single_repo(
    repo_url: str,
    converter: GitHubRepoConverter,
    output_dir: str = None,
    save_skillbook: bool = True,
    verbose: bool = False
) -> ConversionResult:
    """Convert a single repository"""
    repo_name = repo_url.rstrip('/').split('/')[-1]

    if output_dir is None:
        output_dir = f"./converted_repos/{repo_name}"

    print(f"\n🚀 Converting: {repo_url}")
    print(f"📁 Output: {output_dir}")

    result = converter.convert_repo(
        repo_url=repo_url,
        output_dir=output_dir,
        save_skillbook=save_skillbook
    )

    print_conversion_summary(result, verbose=verbose)

    return result


def check_api_key(model: str, api_key: str = None) -> bool:
    """
    Check if appropriate API key is available for the model

    Returns True if API key is available or not required
    """
    # Determine provider from model name
    model_lower = model.lower()

    # Provider-specific checks
    if any(prefix in model_lower for prefix in ['gpt', 'openai/']):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            logger.error("OpenAI API key required for GPT models")
            logger.error("Set OPENAI_API_KEY environment variable or use --api-key")
            return False
    elif any(prefix in model_lower for prefix in ['claude', 'anthropic/']):
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            logger.error("Anthropic API key required for Claude models")
            logger.error("Set ANTHROPIC_API_KEY environment variable or use --api-key")
            return False
    elif any(prefix in model_lower for prefix in ['gemini', 'google/']):
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            logger.error("Google API key required for Gemini models")
            logger.error("Set GOOGLE_API_KEY environment variable or use --api-key")
            return False
    elif 'ollama/' in model_lower:
        # Ollama runs locally, no API key needed
        return True
    else:
        # Unknown provider - warn but continue
        logger.warning(f"Unknown model provider: {model}")
        logger.warning("Make sure you have set the appropriate API key")

    return True


def main():
    """Main CLI entry point"""
    args = parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    # Load environment variables
    load_dotenv()

    # Check for API key based on model
    if not check_api_key(args.model, args.api_key):
        sys.exit(1)

    print("\n" + "="*70)
    print("🤖 ACE GitHub Repo Product Converter")
    print("="*70)

    # Initialize LLM
    print(f"\n⚙️  Initializing LLM: {args.model}")

    # Set API key if provided via argument
    if args.api_key:
        # Determine which environment variable to set based on model
        if 'gpt' in args.model.lower() or 'openai/' in args.model.lower():
            os.environ["OPENAI_API_KEY"] = args.api_key
        elif 'claude' in args.model.lower() or 'anthropic/' in args.model.lower():
            os.environ["ANTHROPIC_API_KEY"] = args.api_key
        elif 'gemini' in args.model.lower() or 'google/' in args.model.lower():
            os.environ["GOOGLE_API_KEY"] = args.api_key

    llm = LiteLLMClient(
        model=args.model,
        temperature=args.temperature
    )

    # Load or create skillbook
    skillbook = None
    if not args.no_learning:
        if os.path.exists(args.skillbook):
            print(f"📚 Loading skillbook: {args.skillbook}")
            skillbook = Skillbook.load_from_file(args.skillbook)
            print(f"   Loaded {len(skillbook.skills)} skills")
        else:
            print(f"📚 Creating new skillbook: {args.skillbook}")
            skillbook = Skillbook()

    # Initialize converter
    converter = GitHubRepoConverter(
        llm_client=llm,
        skillbook=skillbook,
        enable_learning=not args.no_learning
    )

    # Get list of repos to convert
    if args.batch:
        print(f"\n📋 Loading repos from: {args.batch}")
        repo_urls = load_repo_urls_from_file(args.batch)
        print(f"   Found {len(repo_urls)} repositories")
    else:
        repo_urls = [args.repo_url]

    # Convert repositories
    results = []
    for i, repo_url in enumerate(repo_urls, 1):
        print(f"\n{'='*70}")
        print(f"Processing {i}/{len(repo_urls)}")
        print(f"{'='*70}")

        result = convert_single_repo(
            repo_url=repo_url,
            converter=converter,
            output_dir=args.output if len(repo_urls) == 1 else None,
            save_skillbook=args.save_skillbook_per_repo,
            verbose=args.verbose
        )
        results.append(result)

    # Save master skillbook
    if skillbook and not args.no_learning:
        skillbook.save_to_file(args.skillbook)
        print(f"\n📚 Master skillbook saved: {args.skillbook}")
        print(f"   Total skills: {len(skillbook.skills)}")

    # Final summary for batch processing
    if len(results) > 1:
        print("\n" + "="*70)
        print("📊 Batch Conversion Summary")
        print("="*70)

        success_count = len([r for r in results if r.final_status == "success"])
        partial_count = len([r for r in results if r.final_status == "partial"])
        failed_count = len([r for r in results if r.final_status == "failed"])

        print(f"\nTotal repositories: {len(results)}")
        print(f"  ✅ Success: {success_count}")
        print(f"  ⚠️  Partial: {partial_count}")
        print(f"  ❌ Failed: {failed_count}")

        overall_success_rate = success_count / len(results) * 100
        print(f"\nOverall success rate: {overall_success_rate:.1f}%")

    print("\n✨ Conversion complete!")


if __name__ == "__main__":
    main()
