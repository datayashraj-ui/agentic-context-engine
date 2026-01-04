"""
Simple example of using GitHubRepoConverter

Demonstrates how to convert a GitHub repo into a working product using ACE.
"""

import os
from dotenv import load_dotenv

from ace.llm_providers.litellm_client import LiteLLMClient
from ace.integrations.github_repo_converter import GitHubRepoConverter
from ace.skillbook import Skillbook

# Load environment variables
load_dotenv()


def main():
    # Initialize LLM client
    llm = LiteLLMClient(
        model="gpt-4o-mini",  # Fast and cost-effective
        temperature=0.1,
    )

    # Create or load skillbook
    skillbook_path = "repo_converter_skillbook.json"
    if os.path.exists(skillbook_path):
        print(f"Loading existing skillbook from {skillbook_path}")
        skillbook = Skillbook.load_from_file(skillbook_path)
    else:
        print("Creating new skillbook")
        skillbook = Skillbook()

    # Initialize converter
    converter = GitHubRepoConverter(
        llm_client=llm,
        skillbook=skillbook,
        enable_learning=True,
    )

    # Example 1: Convert a small broken Python repo
    print("\n" + "="*60)
    print("Example 1: Converting a sample Python project")
    print("="*60)

    # You can replace this with any GitHub repo URL
    # For demo purposes, we'll show how it would work
    test_repos = [
        "https://github.com/username/broken-project",  # Replace with actual repo
        # Add more repos to process in batch
    ]

    for repo_url in test_repos[:1]:  # Process first repo
        result = converter.convert_repo(
            repo_url=repo_url,
            output_dir=f"./converted_repos/{repo_url.split('/')[-1]}",
            save_skillbook=True,
        )

        # Display results
        print("\nConversion Summary:")
        print(f"  Status: {result.final_status}")
        print(f"  Original issues: {len(result.original_issues)}")
        print(f"  Fixes attempted: {len(result.fixes_attempted)}")
        print(f"  Successful fixes: {len([f for f in result.fixes_attempted if f.success])}")

        if result.skillbook_path:
            print(f"  Skillbook saved: {result.skillbook_path}")

    # Save the master skillbook
    skillbook.save_to_file(skillbook_path)
    print(f"\nMaster skillbook saved to: {skillbook_path}")

    # Display learned skills
    print("\n" + "="*60)
    print("Learned Skills")
    print("="*60)
    print(f"\nTotal skills in skillbook: {len(skillbook.skills)}")
    if skillbook.skills:
        print("\nTop skills:")
        for skill in list(skillbook.skills)[:5]:
            print(f"  - {skill.content[:100]}...")


if __name__ == "__main__":
    main()
