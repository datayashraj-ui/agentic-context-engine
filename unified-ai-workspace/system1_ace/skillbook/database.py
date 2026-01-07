"""
Skillbook database operations

Manages prompt engineering skills with:
- CRUD operations
- Semantic search via embeddings
- Usage tracking
- Success rate calculations
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.database import get_database
from .embeddings import EmbeddingManager


@dataclass
class Skill:
    """Prompt engineering skill/pattern"""
    skill_id: Optional[int] = None
    skill_name: str = ""
    skill_type: str = "pattern"  # template, pattern, technique, domain
    description: str = ""
    prompt_template: str = ""
    metadata: Dict[str, Any] = None
    usage_count: int = 0
    success_rate: float = 0.0
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            k: v for k, v in asdict(self).items()
            if v is not None and k not in ['tags']
        }


class Skillbook:
    """
    Skillbook manager for prompt engineering patterns

    Provides:
    - Add/retrieve/update skills
    - Semantic search using embeddings
    - Usage tracking
    - Success metrics
    """

    def __init__(self):
        self.db = get_database()
        self.embedding_mgr = EmbeddingManager()

    def add_skill(
        self,
        skill_name: str,
        prompt_template: str,
        skill_type: str = "pattern",
        description: str = "",
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Add a new skill to the skillbook

        Args:
            skill_name: Unique name for the skill
            prompt_template: The actual prompt template
            skill_type: Type of skill (template, pattern, technique, domain)
            description: Human-readable description
            tags: List of tags for categorization
            metadata: Additional metadata as JSON

        Returns:
            skill_id of the created skill
        """
        conn = self.db.connect_skillbook()

        # Insert skill
        cursor = conn.execute("""
            INSERT INTO skills (skill_name, skill_type, description, prompt_template, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            skill_name,
            skill_type,
            description,
            prompt_template,
            json.dumps(metadata or {})
        ))

        skill_id = cursor.lastrowid

        # Add tags
        if tags:
            for tag in tags:
                conn.execute("""
                    INSERT INTO skill_tags (skill_id, tag) VALUES (?, ?)
                """, (skill_id, tag))

        conn.commit()

        # Generate and store embedding
        text_for_embedding = f"{skill_name}. {description}. {prompt_template}"
        embedding = self.embedding_mgr.generate_embedding(text_for_embedding)
        self.embedding_mgr.store_embedding(str(skill_id), embedding, {
            "skill_name": skill_name,
            "skill_type": skill_type,
            "description": description
        })

        return skill_id

    def get_skill(self, skill_id: int) -> Optional[Skill]:
        """Get skill by ID"""
        conn = self.db.connect_skillbook()

        cursor = conn.execute("""
            SELECT * FROM skills WHERE skill_id = ?
        """, (skill_id,))

        row = cursor.fetchone()
        if not row:
            return None

        # Get tags
        tags_cursor = conn.execute("""
            SELECT tag FROM skill_tags WHERE skill_id = ?
        """, (skill_id,))
        tags = [row[0] for row in tags_cursor.fetchall()]

        return Skill(
            skill_id=row['skill_id'],
            skill_name=row['skill_name'],
            skill_type=row['skill_type'],
            description=row['description'],
            prompt_template=row['prompt_template'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            usage_count=row['usage_count'],
            success_rate=row['success_rate'],
            version=row['version'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            tags=tags
        )

    def search_skills(
        self,
        query: str,
        skill_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Skill]:
        """
        Search skills using semantic similarity

        Args:
            query: Search query
            skill_type: Filter by skill type
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List of matching skills sorted by relevance
        """
        # Generate query embedding
        query_embedding = self.embedding_mgr.generate_embedding(query)

        # Search in vector database
        results = self.embedding_mgr.search_similar(
            query_embedding,
            limit=limit * 2  # Get more, then filter
        )

        # Get skill IDs from results
        skill_ids = [int(r['id']) for r in results]

        # Fetch skills from database
        conn = self.db.connect_skillbook()

        placeholders = ','.join(['?' for _ in skill_ids])
        query_parts = [f"SELECT * FROM skills WHERE skill_id IN ({placeholders})"]
        params = skill_ids

        if skill_type:
            query_parts.append("AND skill_type = ?")
            params.append(skill_type)

        if tags:
            # Filter by tags (at least one tag must match)
            tags_placeholders = ','.join(['?' for _ in tags])
            query_parts.append(f"""
                AND skill_id IN (
                    SELECT skill_id FROM skill_tags WHERE tag IN ({tags_placeholders})
                )
            """)
            params.extend(tags)

        query_parts.append(f"ORDER BY success_rate DESC, usage_count DESC LIMIT ?")
        params.append(limit)

        cursor = conn.execute(' '.join(query_parts), params)

        skills = []
        for row in cursor.fetchall():
            skills.append(self.get_skill(row['skill_id']))

        return skills

    def update_skill_metrics(self, skill_id: int, was_successful: bool):
        """
        Update skill usage metrics

        Args:
            skill_id: ID of the skill used
            was_successful: Whether the skill usage was successful
        """
        conn = self.db.connect_skillbook()

        # Get current metrics
        cursor = conn.execute("""
            SELECT usage_count, success_rate FROM skills WHERE skill_id = ?
        """, (skill_id,))
        row = cursor.fetchone()

        if not row:
            return

        usage_count = row['usage_count']
        success_rate = row['success_rate']

        # Calculate new metrics
        total_successes = int(usage_count * success_rate)
        if was_successful:
            total_successes += 1

        new_usage_count = usage_count + 1
        new_success_rate = total_successes / new_usage_count if new_usage_count > 0 else 0

        # Update database
        conn.execute("""
            UPDATE skills
            SET usage_count = ?,
                success_rate = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE skill_id = ?
        """, (new_usage_count, new_success_rate, skill_id))

        conn.commit()

    def get_top_skills(
        self,
        limit: int = 10,
        skill_type: Optional[str] = None
    ) -> List[Skill]:
        """Get top-performing skills by success rate"""
        conn = self.db.connect_skillbook()

        query = "SELECT skill_id FROM skills"
        params = []

        if skill_type:
            query += " WHERE skill_type = ?"
            params.append(skill_type)

        query += " ORDER BY success_rate DESC, usage_count DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)

        return [self.get_skill(row['skill_id']) for row in cursor.fetchall()]

    def get_skills_by_tag(self, tag: str) -> List[Skill]:
        """Get all skills with a specific tag"""
        conn = self.db.connect_skillbook()

        cursor = conn.execute("""
            SELECT skill_id FROM skill_tags WHERE tag = ?
        """, (tag,))

        return [self.get_skill(row['skill_id']) for row in cursor.fetchall()]

    def delete_skill(self, skill_id: int) -> bool:
        """Delete a skill from the skillbook"""
        conn = self.db.connect_skillbook()

        conn.execute("DELETE FROM skills WHERE skill_id = ?", (skill_id,))
        conn.commit()

        # Remove from vector database
        self.embedding_mgr.delete_embedding(str(skill_id))

        return True
