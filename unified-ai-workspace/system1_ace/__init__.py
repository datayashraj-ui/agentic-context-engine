"""
System 1: ACE Prompt Engineering Architect

Multi-role LLM architecture for intelligent prompt generation:
- Analyzer: Parses requirements and extracts intent
- Generator: Creates prompt drafts from templates
- Validator: Quality assessment using G-Eval metrics
- Reflector: Generates improvement feedback
- Skill Manager: Retrieves/stores patterns from skillbook

Interactive 6-step dialogue flow with learning loop.
"""

from .agents import (
    AnalyzerAgent,
    GeneratorAgent,
    ValidatorAgent,
    ReflectorAgent,
    SkillManagerAgent
)
from .dialogue import ACEDialogue, RequirementSpec
from .skillbook import Skillbook, Skill

__all__ = [
    "AnalyzerAgent",
    "GeneratorAgent",
    "ValidatorAgent",
    "ReflectorAgent",
    "SkillManagerAgent",
    "ACEDialogue",
    "RequirementSpec",
    "Skillbook",
    "Skill",
]
