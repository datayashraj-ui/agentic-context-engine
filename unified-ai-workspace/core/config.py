"""
Configuration management for Unified AI Workspace

Handles loading and validation of configuration from:
- Environment variables (.env)
- YAML configuration files
- Runtime overrides
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "ollama"  # ollama, lm_studio, llama_cpp
    base_url: str = "http://localhost:11434"
    default_model: str = "qwen2.5:7b"
    function_calling_model: str = "qwen2.5:7b"
    code_model: str = "qwen2.5-coder:7b"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120


@dataclass
class VoiceConfig:
    """Voice pipeline configuration"""
    enabled: bool = True
    tts_engine: str = "indic_parler"  # indic_parler, indicf5, xtts, mms
    stt_engine: str = "indic_conformer"  # indic_conformer, whisper
    default_language: str = "hindi"
    default_voice_gender: str = "female"
    models_path: str = "./voice_models"
    sample_rate: int = 16000


@dataclass
class BrowserConfig:
    """Browser automation configuration"""
    enabled: bool = True
    headless: bool = False
    driver: str = "browser_use"  # browser_use, playwright, selenium
    timeout: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080


@dataclass
class DatabaseConfig:
    """Database configuration"""
    skillbook_path: str = "./data/skillbook.db"
    workspace_path: str = "./data/workspace.db"
    vector_db_path: str = "./data/vector_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8501
    auto_refresh_interval: int = 5  # seconds


@dataclass
class MCPConfig:
    """MCP server configuration"""
    enabled: bool = True
    servers: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class Config:
    """Main configuration class"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)

    # General settings
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    config_dir: str = "./config"

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            llm=LLMConfig(**data.get("llm", {})),
            voice=VoiceConfig(**data.get("voice", {})),
            browser=BrowserConfig(**data.get("browser", {})),
            database=DatabaseConfig(**data.get("database", {})),
            dashboard=DashboardConfig(**data.get("dashboard", {})),
            mcp=MCPConfig(**data.get("mcp", {})),
            debug=data.get("debug", False),
            log_level=data.get("log_level", "INFO"),
            data_dir=data.get("data_dir", "./data"),
            config_dir=data.get("config_dir", "./config"),
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "ollama"),
                base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
                default_model=os.getenv("LLM_DEFAULT_MODEL", "qwen2.5:7b"),
            ),
            voice=VoiceConfig(
                enabled=os.getenv("VOICE_ENABLED", "true").lower() == "true",
                tts_engine=os.getenv("TTS_ENGINE", "indic_parler"),
                stt_engine=os.getenv("STT_ENGINE", "indic_conformer"),
            ),
            browser=BrowserConfig(
                enabled=os.getenv("BROWSER_ENABLED", "true").lower() == "true",
                headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
            ),
            database=DatabaseConfig(
                skillbook_path=os.getenv("SKILLBOOK_PATH", "./data/skillbook.db"),
                workspace_path=os.getenv("WORKSPACE_PATH", "./data/workspace.db"),
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        Path(self.database.vector_db_path).mkdir(parents=True, exist_ok=True)
        Path(self.voice.models_path).mkdir(parents=True, exist_ok=True)


# Global configuration instance
_config: Optional[Config] = None


def load_config(yaml_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment

    Priority: YAML file > Environment variables > Defaults
    """
    global _config

    if _config is not None:
        return _config

    if yaml_path and os.path.exists(yaml_path):
        _config = Config.from_yaml(yaml_path)
    else:
        _config = Config.from_env()

    # Ensure necessary directories exist
    _config.ensure_directories()

    return _config


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
