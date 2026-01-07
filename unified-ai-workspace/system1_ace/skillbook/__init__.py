"""
Skillbook management for ACE Prompt Engineering

Persistent storage of prompt engineering patterns with:
- SQLite for structured data
- Vector embeddings for semantic search
- Usage tracking and success metrics
"""

from .database import Skillbook, Skill
from .embeddings import EmbeddingManager

__all__ = ["Skillbook", "Skill", "EmbeddingManager"]
