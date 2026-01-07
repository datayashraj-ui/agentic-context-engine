"""
Database management for Unified AI Workspace

Provides:
- SQLite database connections for skillbook and workspace
- Schema initialization
- Query helpers
- Vector database integration for embeddings
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import aiosqlite

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .config import get_config


class Database:
    """Main database manager for both systems"""

    def __init__(self, skillbook_path: Optional[str] = None, workspace_path: Optional[str] = None):
        config = get_config()
        self.skillbook_path = skillbook_path or config.database.skillbook_path
        self.workspace_path = workspace_path or config.database.workspace_path

        # Ensure parent directories exist
        Path(self.skillbook_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.workspace_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize connections
        self.skillbook_conn: Optional[sqlite3.Connection] = None
        self.workspace_conn: Optional[sqlite3.Connection] = None

        # Vector database for embeddings
        self.vector_db = None
        if CHROMADB_AVAILABLE:
            self._init_vector_db()

    def _init_vector_db(self):
        """Initialize ChromaDB for embedding storage"""
        config = get_config()
        self.vector_db = chromadb.PersistentClient(
            path=config.database.vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )

    def connect_skillbook(self) -> sqlite3.Connection:
        """Connect to skillbook database"""
        if self.skillbook_conn is None:
            self.skillbook_conn = sqlite3.connect(self.skillbook_path)
            self.skillbook_conn.row_factory = sqlite3.Row
        return self.skillbook_conn

    def connect_workspace(self) -> sqlite3.Connection:
        """Connect to workspace database"""
        if self.workspace_conn is None:
            self.workspace_conn = sqlite3.connect(self.workspace_path)
            self.workspace_conn.row_factory = sqlite3.Row
        return self.workspace_conn

    def init_skillbook_schema(self):
        """Initialize skillbook database schema"""
        conn = self.connect_skillbook()

        conn.executescript("""
        -- Core Skills Table
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL UNIQUE,
            skill_type TEXT CHECK(skill_type IN ('template', 'pattern', 'technique', 'domain')),
            description TEXT,
            prompt_template TEXT NOT NULL,
            metadata TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            version INTEGER DEFAULT 1
        );

        -- Skill Tags for categorization
        CREATE TABLE IF NOT EXISTS skill_tags (
            skill_id INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
            tag TEXT NOT NULL,
            PRIMARY KEY (skill_id, tag)
        );

        -- Learning Sessions
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            task_description TEXT,
            requirement_spec TEXT,  -- JSON
            final_prompt TEXT,
            outcome_rating INTEGER CHECK(outcome_rating BETWEEN 1 AND 5),
            feedback_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            skills_used TEXT  -- JSON array
        );

        -- Validation Reports
        CREATE TABLE IF NOT EXISTS validations (
            validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(session_id),
            prompt_text TEXT,
            clarity_score REAL,
            completeness_score REAL,
            specificity_score REAL,
            coherence_score REAL,
            overall_score REAL,
            feedback TEXT,
            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Extracted Patterns
        CREATE TABLE IF NOT EXISTS extracted_patterns (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(session_id),
            pattern_type TEXT,
            pattern_content TEXT,
            confidence_score REAL,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_skills_type ON skills(skill_type);
        CREATE INDEX IF NOT EXISTS idx_skills_success ON skills(success_rate DESC);
        CREATE INDEX IF NOT EXISTS idx_skills_usage ON skills(usage_count DESC);
        CREATE INDEX IF NOT EXISTS idx_tags_lookup ON skill_tags(tag);
        CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_validations_session ON validations(session_id);
        """)

        conn.commit()

    def init_workspace_schema(self):
        """Initialize workspace database schema"""
        conn = self.connect_workspace()

        conn.executescript("""
        -- AI Employees
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            personality TEXT,
            voice_config TEXT,  -- JSON
            llm_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        );

        -- Agent Runs
        CREATE TABLE IF NOT EXISTS agent_runs (
            run_id TEXT PRIMARY KEY,
            employee_id TEXT REFERENCES employees(employee_id),
            department TEXT,
            task_description TEXT,
            task_type TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed')),
            tokens_used INTEGER DEFAULT 0,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds REAL,
            result TEXT,  -- JSON
            error_message TEXT
        );

        -- Deployed Products
        CREATE TABLE IF NOT EXISTS deployed_products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            deployment_url TEXT,
            repository_url TEXT,
            status TEXT CHECK(status IN ('deploying', 'active', 'paused', 'failed')),
            health_score REAL DEFAULT 1.0,
            last_health_check TIMESTAMP,
            metrics TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deployed_by TEXT REFERENCES employees(employee_id)
        );

        -- Improvement Suggestions
        CREATE TABLE IF NOT EXISTS improvement_suggestions (
            suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT REFERENCES deployed_products(product_id),
            suggested_by TEXT REFERENCES employees(employee_id),
            suggestion_type TEXT,
            description TEXT,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
            status TEXT CHECK(status IN ('pending', 'reviewing', 'approved', 'rejected', 'implemented')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            implemented_at TIMESTAMP
        );

        -- Department Metrics
        CREATE TABLE IF NOT EXISTS department_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL,
            metric_date DATE NOT NULL,
            tasks_completed INTEGER DEFAULT 0,
            tasks_failed INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0.0,
            success_rate REAL DEFAULT 0.0,
            UNIQUE(department, metric_date)
        );

        -- Meeting Logs
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            participants TEXT,  -- JSON array of employee_ids
            discussion_log TEXT,  -- JSON
            decisions TEXT,  -- JSON
            action_items TEXT,  -- JSON
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            duration_minutes REAL
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
        CREATE INDEX IF NOT EXISTS idx_runs_employee ON agent_runs(employee_id);
        CREATE INDEX IF NOT EXISTS idx_runs_status ON agent_runs(status);
        CREATE INDEX IF NOT EXISTS idx_runs_start ON agent_runs(start_time DESC);
        CREATE INDEX IF NOT EXISTS idx_products_status ON deployed_products(status);
        CREATE INDEX IF NOT EXISTS idx_suggestions_product ON improvement_suggestions(product_id);
        CREATE INDEX IF NOT EXISTS idx_suggestions_status ON improvement_suggestions(status);
        CREATE INDEX IF NOT EXISTS idx_metrics_dept_date ON department_metrics(department, metric_date);
        """)

        conn.commit()

    def init_all_schemas(self):
        """Initialize both database schemas"""
        self.init_skillbook_schema()
        self.init_workspace_schema()

    async def async_execute(self, db: str, query: str, params: tuple = ()) -> List[Dict]:
        """Execute async query on specified database"""
        db_path = self.skillbook_path if db == "skillbook" else self.workspace_path

        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    def close(self):
        """Close all database connections"""
        if self.skillbook_conn:
            self.skillbook_conn.close()
        if self.workspace_conn:
            self.workspace_conn.close()


# Global database instance
_database: Optional[Database] = None


def get_database() -> Database:
    """Get the global database instance"""
    global _database
    if _database is None:
        _database = Database()
        _database.init_all_schemas()
    return _database
