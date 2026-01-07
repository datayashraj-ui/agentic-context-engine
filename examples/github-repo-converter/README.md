# GitHub Repo Product Converter

Convert any GitHub repository into a fully functional product using Agentic Context Engineering (ACE).

## What It Does

The GitHubRepoConverter uses ACE to:

1. **Analyze** GitHub repositories to identify issues:
   - Missing dependencies
   - Syntax errors
   - Runtime issues
   - Missing tests
   - Configuration problems

2. **Fix** issues automatically:
   - Create missing dependency files
   - Fix common syntax errors
   - Add basic configurations
   - Generate test scaffolds

3. **Learn** from each conversion:
   - Builds a skillbook of common fixes
   - Improves with each repo processed
   - Adapts to language-specific patterns
   - Handles edge cases through experience

## Quick Start

### Installation

```bash
# Install ACE framework
pip install ace-framework

# Or for development
cd agentic-context-engine
uv sync
```

### Basic Usage

```python
from ace.llm_providers.litellm_client import LiteLLMClient
from ace.integrations.github_repo_converter import GitHubRepoConverter
from ace.skillbook import Skillbook

# Initialize
llm = LiteLLMClient(model="gpt-4o-mini")
converter = GitHubRepoConverter(
    llm_client=llm,
    skillbook=Skillbook(),
    enable_learning=True
)

# Convert a repo
result = converter.convert_repo(
    repo_url="https://github.com/user/broken-project",
    output_dir="./fixed_project"
)

print(f"Status: {result.final_status}")
print(f"Issues fixed: {len([f for f in result.fixes_attempted if f.success])}")
```

### CLI Usage

```bash
# Convert a single repo
python scripts/repo_converter_cli.py https://github.com/user/repo

# With custom output directory
python scripts/repo_converter_cli.py https://github.com/user/repo --output ./my_project

# Batch convert multiple repos
python scripts/repo_converter_cli.py --batch repos.txt

# Use specific model
python scripts/repo_converter_cli.py https://github.com/user/repo --model gpt-4

# Verbose output
python scripts/repo_converter_cli.py https://github.com/user/repo --verbose
```

## Features

### Current Capabilities

✅ **Python Projects**
- Detect missing `requirements.txt` or `pyproject.toml`
- Extract dependencies from imports
- Check for syntax errors
- Verify test suite presence

✅ **JavaScript/TypeScript Projects**
- Detect missing `package.json`
- Identify dependency issues
- Check for syntax errors

✅ **Learning System**
- Builds skillbook from successful fixes
- Learns language-specific patterns
- Improves over time
- Shares knowledge across repos

### Planned Features

🚧 **Extended Language Support**
- Go, Rust, Java support
- Framework-specific fixes (React, Django, etc.)

🚧 **Advanced Fixes**
- Automated dependency updates
- Breaking change migrations
- Performance optimizations
- Security vulnerability fixes

🚧 **Testing & CI/CD**
- Auto-generate test suites
- Configure CI/CD pipelines
- Run and fix failing tests

🚧 **Documentation**
- Generate/improve README
- Add code comments
- Create API documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHubRepoConverter                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Clone Repo ──────────────────────────────────────┐     │
│                                                       │     │
│  2. RepoAnalyzer ─────────────────────────────┐      │     │
│     - Detect language                         │      │     │
│     - Check dependencies                      │      │     │
│     - Find syntax errors                      │      │     │
│     - Analyze tests                           │      │     │
│     └───────────► [List of Issues]            │      │     │
│                                                │      │     │
│  3. RepoFixer ────────────────────────────────┘      │     │
│     - Apply automatic fixes                          │     │
│     - Track success/failure                          │     │
│     └───────────► [Fix Attempts]                     │     │
│                                                       │     │
│  4. ACE Learning Loop ────────────────────────────────┘     │
│     - Reflector analyzes results                           │
│     - SkillManager updates skillbook                       │
│     - Improves for next conversion                         │
│                                                             │
│  5. Output ─────────────────────────────────────────────┐   │
│     - Fixed repository                                  │   │
│     - Conversion report                                 │   │
│     - Updated skillbook                                 │   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Examples

### Example 1: Fix a Broken Python Project

```python
# simple_converter_example.py
from ace.llm_providers.litellm_client import LiteLLMClient
from ace.integrations.github_repo_converter import GitHubRepoConverter
from ace.skillbook import Skillbook

llm = LiteLLMClient(model="gpt-4o-mini")
converter = GitHubRepoConverter(llm_client=llm, enable_learning=True)

result = converter.convert_repo(
    repo_url="https://github.com/username/broken-python-project",
    output_dir="./fixed_project"
)

print(f"✅ Conversion complete!")
print(f"Issues found: {len(result.original_issues)}")
print(f"Fixes applied: {len([f for f in result.fixes_attempted if f.success])}")
```

### Example 2: Batch Process Multiple Repos

Create a file `repos.txt`:
```
https://github.com/user/project1
https://github.com/user/project2
https://github.com/user/project3
```

Run the CLI:
```bash
python scripts/repo_converter_cli.py --batch repos.txt --model gpt-4o-mini
```

### Example 3: Build Expertise Over Time

```python
from ace.skillbook import Skillbook
from ace.integrations.github_repo_converter import GitHubRepoConverter
from ace.llm_providers.litellm_client import LiteLLMClient

# Load existing skillbook (or create new)
skillbook = Skillbook.load_from_file("converter_skills.json")
print(f"Starting with {len(skillbook.skills)} skills")

llm = LiteLLMClient(model="gpt-4o-mini")
converter = GitHubRepoConverter(llm, skillbook=skillbook)

# Process multiple repos - learning from each
repos = [
    "https://github.com/user/repo1",
    "https://github.com/user/repo2",
    "https://github.com/user/repo3",
]

for repo in repos:
    result = converter.convert_repo(repo)
    print(f"Processed {repo}: {result.final_status}")

# Save accumulated knowledge
skillbook.save_to_file("converter_skills.json")
print(f"Ending with {len(skillbook.skills)} skills (learned from {len(repos)} repos)")
```

## Use Cases

### 1. **Legacy Code Modernization**
Convert old, unmaintained repos into working projects:
- Fix deprecated dependencies
- Update to modern language versions
- Add missing configurations

### 2. **Tutorial/Example Projects**
Ensure educational repos work out-of-the-box:
- Fix broken dependencies
- Add missing setup instructions
- Verify examples run successfully

### 3. **Open Source Triage**
Quickly assess and fix common issues in OSS projects:
- Auto-fix simple issues before manual review
- Generate issue reports for complex problems
- Batch process PRs for dependency updates

### 4. **DevOps Automation**
Automate repository health checks:
- Validate new repos meet standards
- Fix common setup issues
- Ensure CI/CD configurations are present

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your-api-key"

# Optional - use other providers
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Model Selection

- **gpt-4o-mini**: Fast, cost-effective (recommended)
- **gpt-4**: More capable for complex fixes
- **claude-3-5-sonnet-20241022**: Alternative provider
- **ollama/codellama**: Local model (free but slower)

## Limitations

**Current Limitations:**
- Only Python and JavaScript fully supported
- Automatic fixes limited to common issues
- Complex bugs require manual intervention
- No GUI (CLI and Python API only)

**Not Suitable For:**
- Large enterprise codebases (>10K files)
- Repos requiring domain expertise
- Security-critical production systems

## Contributing

We welcome contributions! Areas for improvement:

1. **Language Support**: Add Go, Rust, Java analyzers
2. **Fix Strategies**: Implement more sophisticated fixes
3. **Test Generation**: Auto-create test suites
4. **Documentation**: Generate/improve READMEs

See `CONTRIBUTING.md` for guidelines.

## License

MIT License - see LICENSE file for details.

## Citation

If you use this tool in research, please cite:

```bibtex
@article{ace2024,
  title={Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models},
  author={Your Name},
  journal={arXiv preprint arXiv:2510.04618},
  year={2024}
}
```
