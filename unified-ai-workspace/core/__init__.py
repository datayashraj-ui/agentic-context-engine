"""
Core infrastructure for Unified AI Workspace

This module provides foundational components shared across both systems:
- Database connections and schemas
- LLM client management (Ollama, LM Studio, llama.cpp)
- Configuration management
- Logging utilities
"""

from .config import Config, load_config
from .database import Database, get_database
from .llm_manager import LLMManager, get_llm

__all__ = [
    "Config",
    "load_config",
    "Database",
    "get_database",
    "LLMManager",
    "get_llm",
]
