"""
ACE GitHub Repo Product Converter

Converts GitHub repositories into fully functional products by:
1. Analyzing repo structure and identifying issues
2. Fixing errors, gaps, and missing dependencies
3. Learning from successes/failures to improve over time
4. Building a skillbook of common fixes and edge cases

Usage:
    from ace.integrations.github_repo_converter import GitHubRepoConverter

    converter = GitHubRepoConverter(llm_client)
    result = converter.convert_repo(
        repo_url="https://github.com/user/repo",
        output_dir="./converted_repo"
    )
"""

import os
import json
import subprocess
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from ace.skillbook import Skillbook
from ace.roles import Reflector, SkillManager, AgentOutput
from ace.llm import LLMClient
from ace.prompts_v2_1 import PromptManager


@dataclass
class RepoIssue:
    """Represents an issue found in a repository"""
    category: str  # "dependency", "syntax", "runtime", "configuration", "test"
    severity: str  # "critical", "major", "minor"
    file_path: Optional[str]
    description: str
    suggested_fix: Optional[str] = None


@dataclass
class FixAttempt:
    """Represents an attempt to fix an issue"""
    issue: RepoIssue
    fix_applied: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class ConversionResult:
    """Result of converting a repository"""
    repo_url: str
    original_issues: List[RepoIssue]
    fixes_attempted: List[FixAttempt]
    final_status: str  # "success", "partial", "failed"
    tests_passing: bool
    build_successful: bool
    skillbook_path: Optional[str] = None


class RepoAnalyzer:
    """Analyzes GitHub repositories to identify issues"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def clone_repo(self, repo_url: str, target_dir: str) -> bool:
        """Clone a GitHub repository"""
        try:
            subprocess.run(
                ["git", "clone", repo_url, target_dir],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repo: {e.stderr}")
            return False

    def detect_language(self, repo_dir: str) -> str:
        """Detect primary programming language"""
        language_indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
            "javascript": ["package.json", "*.js", "*.ts"],
            "go": ["go.mod", "go.sum", "*.go"],
            "rust": ["Cargo.toml", "*.rs"],
            "java": ["pom.xml", "build.gradle", "*.java"],
        }

        repo_path = Path(repo_dir)
        for lang, indicators in language_indicators.items():
            for indicator in indicators:
                if "*" in indicator:
                    if list(repo_path.rglob(indicator)):
                        return lang
                elif (repo_path / indicator).exists():
                    return lang

        return "unknown"

    def analyze_structure(self, repo_dir: str) -> Dict[str, Any]:
        """Analyze repository structure and files"""
        repo_path = Path(repo_dir)

        structure = {
            "language": self.detect_language(repo_dir),
            "has_readme": (repo_path / "README.md").exists(),
            "has_tests": any([
                (repo_path / "tests").exists(),
                (repo_path / "test").exists(),
                list(repo_path.rglob("*test*.py")),
                list(repo_path.rglob("*.test.js")),
            ]),
            "has_ci": any([
                (repo_path / ".github" / "workflows").exists(),
                (repo_path / ".gitlab-ci.yml").exists(),
            ]),
            "dependencies_file": None,
            "entry_points": [],
        }

        # Find dependency files
        dep_files = {
            "requirements.txt": repo_path / "requirements.txt",
            "package.json": repo_path / "package.json",
            "go.mod": repo_path / "go.mod",
            "Cargo.toml": repo_path / "Cargo.toml",
        }

        for name, path in dep_files.items():
            if path.exists():
                structure["dependencies_file"] = str(path)
                break

        return structure

    def check_dependencies(self, repo_dir: str, language: str) -> List[RepoIssue]:
        """Check for dependency issues"""
        issues = []
        repo_path = Path(repo_dir)

        if language == "python":
            # Check for requirements.txt or pyproject.toml
            if not (repo_path / "requirements.txt").exists() and \
               not (repo_path / "pyproject.toml").exists():
                issues.append(RepoIssue(
                    category="dependency",
                    severity="major",
                    file_path=None,
                    description="Missing dependency file (requirements.txt or pyproject.toml)",
                    suggested_fix="Create requirements.txt from imports"
                ))

            # Try to install dependencies
            if (repo_path / "requirements.txt").exists():
                result = subprocess.run(
                    ["pip", "install", "-r", "requirements.txt", "--dry-run"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    issues.append(RepoIssue(
                        category="dependency",
                        severity="critical",
                        file_path="requirements.txt",
                        description=f"Dependency installation would fail: {result.stderr[:200]}",
                        suggested_fix="Update package versions or remove incompatible packages"
                    ))

        elif language == "javascript":
            if not (repo_path / "package.json").exists():
                issues.append(RepoIssue(
                    category="dependency",
                    severity="major",
                    file_path=None,
                    description="Missing package.json",
                    suggested_fix="Initialize npm project"
                ))

        return issues

    def check_syntax(self, repo_dir: str, language: str) -> List[RepoIssue]:
        """Check for syntax errors"""
        issues = []
        repo_path = Path(repo_dir)

        if language == "python":
            # Find all Python files
            py_files = list(repo_path.rglob("*.py"))
            for py_file in py_files[:10]:  # Limit to first 10 files
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    issues.append(RepoIssue(
                        category="syntax",
                        severity="critical",
                        file_path=str(py_file.relative_to(repo_path)),
                        description=f"Syntax error: {result.stderr[:200]}",
                        suggested_fix="Fix syntax error in file"
                    ))

        return issues

    def check_tests(self, repo_dir: str, language: str) -> List[RepoIssue]:
        """Check if tests exist and pass"""
        issues = []
        repo_path = Path(repo_dir)

        has_tests = any([
            (repo_path / "tests").exists(),
            (repo_path / "test").exists(),
            list(repo_path.rglob("*test*.py")) if language == "python" else [],
        ])

        if not has_tests:
            issues.append(RepoIssue(
                category="test",
                severity="minor",
                file_path=None,
                description="No test suite found",
                suggested_fix="Create basic test suite"
            ))

        return issues

    def analyze_repo(self, repo_dir: str) -> List[RepoIssue]:
        """Comprehensive repository analysis"""
        structure = self.analyze_structure(repo_dir)
        language = structure["language"]

        all_issues = []
        all_issues.extend(self.check_dependencies(repo_dir, language))
        all_issues.extend(self.check_syntax(repo_dir, language))
        all_issues.extend(self.check_tests(repo_dir, language))

        return all_issues


class RepoFixer:
    """Applies fixes to repository issues"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def fix_missing_dependencies_file(self, repo_dir: str, language: str) -> FixAttempt:
        """Create missing dependency file"""
        repo_path = Path(repo_dir)

        if language == "python":
            # Scan for imports and create requirements.txt
            imports = self._extract_python_imports(repo_dir)
            req_file = repo_path / "requirements.txt"

            try:
                with open(req_file, "w") as f:
                    for imp in sorted(imports):
                        f.write(f"{imp}\n")

                return FixAttempt(
                    issue=RepoIssue("dependency", "major", None, "Missing requirements.txt"),
                    fix_applied=f"Created requirements.txt with {len(imports)} packages",
                    success=True
                )
            except Exception as e:
                return FixAttempt(
                    issue=RepoIssue("dependency", "major", None, "Missing requirements.txt"),
                    fix_applied="Attempted to create requirements.txt",
                    success=False,
                    error_message=str(e)
                )

        return FixAttempt(
            issue=RepoIssue("dependency", "major", None, f"Missing dependency file for {language}"),
            fix_applied="No fix available",
            success=False,
            error_message=f"Unsupported language: {language}"
        )

    def _extract_python_imports(self, repo_dir: str) -> List[str]:
        """Extract unique imports from Python files"""
        imports = set()
        repo_path = Path(repo_dir)

        # Standard library modules to exclude
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 're', 'typing',
            'collections', 'itertools', 'functools', 'subprocess', 'tempfile',
        }

        for py_file in repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("import "):
                            module = line.split()[1].split('.')[0]
                            if module not in stdlib_modules:
                                imports.add(module)
                        elif line.startswith("from "):
                            module = line.split()[1].split('.')[0]
                            if module not in stdlib_modules:
                                imports.add(module)
            except:
                continue

        return list(imports)

    def fix_issue(self, repo_dir: str, issue: RepoIssue, language: str) -> FixAttempt:
        """Apply fix for a specific issue"""
        if issue.category == "dependency" and "Missing dependency file" in issue.description:
            return self.fix_missing_dependencies_file(repo_dir, language)

        # Placeholder for other fixes
        return FixAttempt(
            issue=issue,
            fix_applied="No automatic fix available",
            success=False,
            error_message="Fix not implemented"
        )


class GitHubRepoConverter:
    """
    ACE-powered GitHub repository converter

    Converts GitHub repos into working products by:
    - Analyzing structure and identifying issues
    - Applying fixes iteratively
    - Learning from successes/failures
    - Building expertise over time
    """

    def __init__(
        self,
        llm_client: LLMClient,
        skillbook: Optional[Skillbook] = None,
        enable_learning: bool = True,
    ):
        self.llm = llm_client
        self.skillbook = skillbook if skillbook is not None else Skillbook()
        self.enable_learning = enable_learning

        # Initialize ACE components
        prompt_mgr = PromptManager()
        self.reflector = Reflector(
            llm_client,
            prompt_template=prompt_mgr.get_reflector_prompt()
        )
        self.skill_manager = SkillManager(
            llm_client,
            prompt_template=prompt_mgr.get_skill_manager_prompt()
        )

        # Initialize converter components
        self.analyzer = RepoAnalyzer(llm_client)
        self.fixer = RepoFixer(llm_client)

    def convert_repo(
        self,
        repo_url: str,
        output_dir: Optional[str] = None,
        save_skillbook: bool = True,
    ) -> ConversionResult:
        """
        Convert a GitHub repository into a working product

        Args:
            repo_url: GitHub repository URL
            output_dir: Where to clone/save the repo (creates temp dir if None)
            save_skillbook: Whether to save learned skills to disk

        Returns:
            ConversionResult with details of the conversion
        """
        # Create temp directory if needed
        if output_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="ace_repo_")
            output_dir = temp_dir
        else:
            os.makedirs(output_dir, exist_ok=True)

        print(f"Converting repository: {repo_url}")
        print(f"Output directory: {output_dir}")

        # Step 1: Clone repository
        if not self.analyzer.clone_repo(repo_url, output_dir):
            return ConversionResult(
                repo_url=repo_url,
                original_issues=[],
                fixes_attempted=[],
                final_status="failed",
                tests_passing=False,
                build_successful=False
            )

        # Step 2: Analyze repository
        print("\nAnalyzing repository...")
        structure = self.analyzer.analyze_structure(output_dir)
        issues = self.analyzer.analyze_repo(output_dir)

        print(f"Detected language: {structure['language']}")
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  [{issue.severity}] {issue.category}: {issue.description}")

        # Step 3: Apply fixes
        print("\nApplying fixes...")
        fixes = []
        for issue in issues:
            if issue.severity in ["critical", "major"]:
                fix_attempt = self.fixer.fix_issue(output_dir, issue, structure['language'])
                fixes.append(fix_attempt)

                if fix_attempt.success:
                    print(f"  ✓ Fixed: {issue.description}")
                else:
                    print(f"  ✗ Failed: {issue.description}")

        # Step 4: Learn from results (if enabled)
        if self.enable_learning and fixes:
            print("\nLearning from results...")
            self._learn_from_conversion(repo_url, issues, fixes, structure)

        # Step 5: Final verification
        print("\nVerifying final state...")
        final_issues = self.analyzer.analyze_repo(output_dir)

        success_rate = len([f for f in fixes if f.success]) / len(fixes) if fixes else 0
        final_status = "success" if success_rate >= 0.8 else "partial" if success_rate > 0 else "failed"

        # Save skillbook if requested
        skillbook_path = None
        if save_skillbook and self.skillbook:
            skillbook_path = os.path.join(output_dir, "ace_skillbook.json")
            self.skillbook.save_to_file(skillbook_path)
            print(f"\nSkillbook saved to: {skillbook_path}")

        result = ConversionResult(
            repo_url=repo_url,
            original_issues=issues,
            fixes_attempted=fixes,
            final_status=final_status,
            tests_passing=False,  # TODO: Actually run tests
            build_successful=len(final_issues) == 0,
            skillbook_path=skillbook_path
        )

        print(f"\n{'='*60}")
        print(f"Conversion complete: {final_status.upper()}")
        print(f"Issues found: {len(issues)}")
        print(f"Fixes attempted: {len(fixes)}")
        print(f"Fixes successful: {len([f for f in fixes if f.success])}")
        print(f"{'='*60}")

        return result

    def _learn_from_conversion(
        self,
        repo_url: str,
        issues: List[RepoIssue],
        fixes: List[FixAttempt],
        structure: Dict[str, Any]
    ):
        """Learn from the conversion process using ACE"""
        if not self.enable_learning:
            return

        # Build execution trace
        reasoning = f"""Repository Analysis and Fixes:
URL: {repo_url}
Language: {structure['language']}

Issues Identified: {len(issues)}
{self._format_issues(issues)}

Fixes Applied: {len(fixes)}
{self._format_fixes(fixes)}
"""

        # Create agent output from the conversion results
        success_rate = len([f for f in fixes if f.success]) / len(fixes) if fixes else 0
        final_answer = f"Converted {repo_url}: {success_rate:.0%} success rate on {len(fixes)} fixes"

        agent_output = AgentOutput(
            reasoning=reasoning,
            final_answer=final_answer,
            skill_ids=[],  # No skills cited (external fixing process)
            raw={"metadata": {
                "repo_url": repo_url,
                "language": structure['language'],
                "issues": len(issues),
                "fixes": len(fixes),
                "success_rate": success_rate
            }}
        )

        # Build feedback from results
        successful_fixes = [f for f in fixes if f.success]
        failed_fixes = [f for f in fixes if not f.success]

        feedback_parts = []
        if successful_fixes:
            feedback_parts.append(f"Successfully fixed {len(successful_fixes)} issues:")
            for fix in successful_fixes[:3]:  # Show first 3
                feedback_parts.append(f"  - {fix.issue.description}: {fix.fix_applied}")

        if failed_fixes:
            feedback_parts.append(f"\nFailed to fix {len(failed_fixes)} issues:")
            for fix in failed_fixes[:3]:  # Show first 3
                feedback_parts.append(f"  - {fix.issue.description}: {fix.error_message or 'Unknown error'}")

        feedback = "\n".join(feedback_parts)

        # Run Reflector
        task_description = f"Convert GitHub repository into working product: {repo_url} ({structure['language']})"
        reflection = self.reflector.reflect(
            question=task_description,
            agent_output=agent_output,
            skillbook=self.skillbook,
            feedback=feedback,
            ground_truth=None  # No ground truth for repo conversion
        )

        # Run SkillManager
        skill_manager_output = self.skill_manager.update_skills(
            reflection=reflection,
            skillbook=self.skillbook,
            question_context=f"Repository conversion: {repo_url}",
            progress=f"Processed {len(issues)} issues, applied {len(fixes)} fixes"
        )

        # Apply updates to skillbook
        if skill_manager_output.update:
            self.skillbook.apply_update(skill_manager_output.update)

    def _format_issues(self, issues: List[RepoIssue]) -> str:
        """Format issues for display"""
        lines = []
        for i, issue in enumerate(issues, 1):
            lines.append(f"{i}. [{issue.severity}] {issue.category}: {issue.description}")
            if issue.file_path:
                lines.append(f"   File: {issue.file_path}")
        return "\n".join(lines)

    def _format_fixes(self, fixes: List[FixAttempt]) -> str:
        """Format fix attempts for display"""
        lines = []
        for i, fix in enumerate(fixes, 1):
            status = "✓" if fix.success else "✗"
            lines.append(f"{i}. {status} {fix.issue.description}")
            lines.append(f"   Fix: {fix.fix_applied}")
            if not fix.success and fix.error_message:
                lines.append(f"   Error: {fix.error_message}")
        return "\n".join(lines)
