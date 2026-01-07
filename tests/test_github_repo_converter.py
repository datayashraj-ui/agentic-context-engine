"""
Tests for GitHubRepoConverter integration
"""

import unittest
import tempfile
import os
from pathlib import Path

from ace.llm import DummyLLMClient
from ace.integrations.github_repo_converter import (
    GitHubRepoConverter,
    RepoAnalyzer,
    RepoFixer,
    RepoIssue,
)
from ace.skillbook import Skillbook


class TestRepoAnalyzer(unittest.TestCase):
    """Test RepoAnalyzer functionality"""

    def setUp(self):
        self.llm = DummyLLMClient()
        self.analyzer = RepoAnalyzer(self.llm)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Cleanup temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_detect_language_python(self):
        """Test Python language detection"""
        # Create a Python project structure
        (Path(self.temp_dir) / "requirements.txt").touch()
        (Path(self.temp_dir) / "main.py").touch()

        language = self.analyzer.detect_language(self.temp_dir)
        self.assertEqual(language, "python")

    def test_detect_language_javascript(self):
        """Test JavaScript language detection"""
        # Create a JavaScript project structure
        (Path(self.temp_dir) / "package.json").touch()

        language = self.analyzer.detect_language(self.temp_dir)
        self.assertEqual(language, "javascript")

    def test_analyze_structure_python(self):
        """Test structure analysis for Python project"""
        # Create a Python project
        (Path(self.temp_dir) / "requirements.txt").touch()
        (Path(self.temp_dir) / "README.md").touch()
        os.makedirs(Path(self.temp_dir) / "tests", exist_ok=True)

        structure = self.analyzer.analyze_structure(self.temp_dir)

        self.assertEqual(structure["language"], "python")
        self.assertTrue(structure["has_readme"])
        self.assertTrue(structure["has_tests"])
        self.assertIsNotNone(structure["dependencies_file"])

    def test_check_dependencies_missing(self):
        """Test detection of missing dependency file"""
        # Python project without requirements.txt
        (Path(self.temp_dir) / "main.py").touch()

        issues = self.analyzer.check_dependencies(self.temp_dir, "python")

        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Missing dependency file" in issue.description for issue in issues))

    def test_check_syntax_valid_python(self):
        """Test syntax checking for valid Python file"""
        # Create a valid Python file
        py_file = Path(self.temp_dir) / "valid.py"
        py_file.write_text("def hello():\n    print('Hello, World!')\n")

        issues = self.analyzer.check_syntax(self.temp_dir, "python")

        # Should have no syntax errors
        self.assertEqual(len(issues), 0)

    def test_check_syntax_invalid_python(self):
        """Test syntax checking for invalid Python file"""
        # Create an invalid Python file
        py_file = Path(self.temp_dir) / "invalid.py"
        py_file.write_text("def hello(\n    print('Missing closing paren')\n")

        issues = self.analyzer.check_syntax(self.temp_dir, "python")

        # Should detect syntax error
        self.assertGreater(len(issues), 0)
        self.assertTrue(any(issue.category == "syntax" for issue in issues))


class TestRepoFixer(unittest.TestCase):
    """Test RepoFixer functionality"""

    def setUp(self):
        self.llm = DummyLLMClient()
        self.fixer = RepoFixer(self.llm)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_extract_python_imports(self):
        """Test extraction of Python imports"""
        # Create Python files with imports
        py_file = Path(self.temp_dir) / "example.py"
        py_file.write_text("""
import requests
from flask import Flask
import os
from typing import List
import numpy as np
""")

        imports = self.fixer._extract_python_imports(self.temp_dir)

        # Should extract third-party packages, not stdlib
        self.assertIn("requests", imports)
        self.assertIn("flask", imports)
        self.assertIn("numpy", imports)
        self.assertNotIn("os", imports)  # stdlib
        self.assertNotIn("typing", imports)  # stdlib

    def test_fix_missing_dependencies_file(self):
        """Test creation of requirements.txt"""
        # Create Python file with imports
        py_file = Path(self.temp_dir) / "app.py"
        py_file.write_text("import requests\nfrom flask import Flask\n")

        fix_attempt = self.fixer.fix_missing_dependencies_file(self.temp_dir, "python")

        self.assertTrue(fix_attempt.success)
        self.assertTrue((Path(self.temp_dir) / "requirements.txt").exists())

        # Check contents
        req_content = (Path(self.temp_dir) / "requirements.txt").read_text()
        self.assertIn("requests", req_content)
        self.assertIn("flask", req_content)


class TestGitHubRepoConverter(unittest.TestCase):
    """Test GitHubRepoConverter integration"""

    def setUp(self):
        self.llm = DummyLLMClient()
        self.skillbook = Skillbook()
        self.converter = GitHubRepoConverter(
            llm_client=self.llm,
            skillbook=self.skillbook,
            enable_learning=True
        )

    def test_initialization(self):
        """Test converter initialization"""
        self.assertIsNotNone(self.converter.analyzer)
        self.assertIsNotNone(self.converter.fixer)
        self.assertIsNotNone(self.converter.reflector)
        self.assertIsNotNone(self.converter.skill_manager)
        self.assertTrue(self.converter.enable_learning)

    def test_format_issues(self):
        """Test issue formatting"""
        issues = [
            RepoIssue(
                category="dependency",
                severity="major",
                file_path="requirements.txt",
                description="Missing dependency"
            ),
            RepoIssue(
                category="syntax",
                severity="critical",
                file_path="main.py",
                description="Syntax error on line 10"
            )
        ]

        formatted = self.converter._format_issues(issues)

        self.assertIn("dependency", formatted)
        self.assertIn("syntax", formatted)
        self.assertIn("major", formatted)
        self.assertIn("critical", formatted)

    def test_skillbook_integration(self):
        """Test that skillbook is properly integrated"""
        # Converter should have access to skillbook
        self.assertIsNotNone(self.converter.skillbook)
        self.assertEqual(self.converter.skillbook, self.skillbook)

    def test_learning_disabled(self):
        """Test converter with learning disabled"""
        converter_no_learning = GitHubRepoConverter(
            llm_client=self.llm,
            enable_learning=False
        )

        self.assertFalse(converter_no_learning.enable_learning)


if __name__ == "__main__":
    unittest.main()
