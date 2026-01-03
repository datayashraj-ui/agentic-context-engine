"""
Security Orchestrator

Coordinates all security agents and manages:
- Threat detection
- Automated remediation
- Incident response
- Real-time monitoring
- Compliance tracking
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio

from core import get_database, get_llm


class ThreatSeverity(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatCategory(Enum):
    """Threat categories"""
    CODE_INJECTION = "code_injection"
    AUTHENTICATION = "authentication"
    DATA_SECURITY = "data_security"
    API_SECURITY = "api_security"
    LOGIC_FLAW = "logic_flaw"
    DEPENDENCY = "dependency"
    INFRASTRUCTURE = "infrastructure"
    AI_LLM = "ai_llm"
    SOCIAL_ENGINEERING = "social_engineering"
    MOBILE = "mobile"
    WEB = "web"
    COMPLIANCE = "compliance"


@dataclass
class ThreatDetection:
    """Detected threat"""
    threat_id: str
    category: ThreatCategory
    severity: ThreatSeverity
    title: str
    description: str
    affected_file: Optional[str] = None
    affected_line: Optional[int] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration
    cvss_score: Optional[float] = None  # Common Vulnerability Scoring System
    remediation: Optional[str] = None
    detected_at: datetime = None
    auto_fixable: bool = False

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()


@dataclass
class RemediationAction:
    """Automated remediation action"""
    action_id: str
    threat_id: str
    action_type: str  # fix, quarantine, block, alert
    description: str
    applied: bool = False
    success: bool = False
    error_message: Optional[str] = None


class SecurityOrchestrator:
    """
    Central security orchestration system

    Manages all security agents and coordinates:
    - Threat detection across all agents
    - Automated remediation
    - Incident response workflows
    - Real-time monitoring
    - Compliance reporting
    """

    def __init__(self):
        self.db = get_database()
        self.llm = get_llm()
        self.agents = {}
        self.active_threats = []
        self.is_monitoring = False

        # Initialize database schema
        self._init_security_schema()

        # Load agents
        self._load_agents()

    def _init_security_schema(self):
        """Initialize security database tables"""
        conn = self.db.connect_workspace()

        conn.executescript("""
        -- Threat detections
        CREATE TABLE IF NOT EXISTS security_threats (
            threat_id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            affected_file TEXT,
            affected_line INTEGER,
            cwe_id TEXT,
            cvss_score REAL,
            remediation TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            auto_fixable BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'false_positive'))
        );

        -- Remediation actions
        CREATE TABLE IF NOT EXISTS security_remediations (
            action_id TEXT PRIMARY KEY,
            threat_id TEXT REFERENCES security_threats(threat_id),
            action_type TEXT NOT NULL,
            description TEXT,
            applied BOOLEAN DEFAULT 0,
            success BOOLEAN DEFAULT 0,
            error_message TEXT,
            applied_at TIMESTAMP
        );

        -- Security scans
        CREATE TABLE IF NOT EXISTS security_scans (
            scan_id TEXT PRIMARY KEY,
            scan_type TEXT NOT NULL,
            target TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            threats_found INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running'
        );

        -- Compliance checks
        CREATE TABLE IF NOT EXISTS compliance_checks (
            check_id TEXT PRIMARY KEY,
            framework TEXT NOT NULL,  -- GDPR, HIPAA, PCI-DSS, SOC2
            requirement TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pass', 'fail', 'warning', 'not_applicable')),
            details TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Security metrics
        CREATE TABLE IF NOT EXISTS security_metrics (
            metric_date DATE PRIMARY KEY,
            threats_detected INTEGER DEFAULT 0,
            threats_critical INTEGER DEFAULT 0,
            threats_resolved INTEGER DEFAULT 0,
            scans_completed INTEGER DEFAULT 0,
            compliance_score REAL DEFAULT 1.0
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_threats_severity ON security_threats(severity);
        CREATE INDEX IF NOT EXISTS idx_threats_status ON security_threats(status);
        CREATE INDEX IF NOT EXISTS idx_threats_detected ON security_threats(detected_at DESC);
        CREATE INDEX IF NOT EXISTS idx_scans_completed ON security_scans(completed_at DESC);
        """)

        conn.commit()

    def _load_agents(self):
        """Load all security agents"""
        from .agents.code_injection_guard import CodeInjectionGuard
        from .agents.authentication_shield import AuthenticationShield
        from .agents.data_protection_agent import DataProtectionAgent
        from .agents.dependency_scanner import DependencyScanner

        self.agents = {
            "code_injection": CodeInjectionGuard(self),
            "authentication": AuthenticationShield(self),
            "data_protection": DataProtectionAgent(self),
            "dependency": DependencyScanner(self),
        }

    async def scan_code(self, code: str, file_path: Optional[str] = None) -> List[ThreatDetection]:
        """
        Comprehensive security scan of code

        Args:
            code: Source code to scan
            file_path: Optional file path for context

        Returns:
            List of detected threats
        """
        scan_id = f"scan_{datetime.now().timestamp()}"
        threats = []

        # Start scan record
        conn = self.db.connect_workspace()
        conn.execute("""
            INSERT INTO security_scans (scan_id, scan_type, target, started_at)
            VALUES (?, 'code', ?, CURRENT_TIMESTAMP)
        """, (scan_id, file_path or "inline"))
        conn.commit()

        # Run all agents concurrently
        scan_tasks = []
        for agent_name, agent in self.agents.items():
            scan_tasks.append(agent.scan(code, file_path))

        results = await asyncio.gather(*scan_tasks, return_exceptions=True)

        # Collect threats
        for result in results:
            if isinstance(result, Exception):
                print(f"Agent scan failed: {result}")
                continue
            threats.extend(result)

        # Update scan record
        conn.execute("""
            UPDATE security_scans
            SET completed_at = CURRENT_TIMESTAMP,
                threats_found = ?,
                status = 'completed'
            WHERE scan_id = ?
        """, (len(threats), scan_id))

        # Store threats
        for threat in threats:
            self._store_threat(threat)

        conn.commit()

        return threats

    def _store_threat(self, threat: ThreatDetection):
        """Store threat in database"""
        conn = self.db.connect_workspace()

        conn.execute("""
            INSERT INTO security_threats (
                threat_id, category, severity, title, description,
                affected_file, affected_line, cwe_id, cvss_score,
                remediation, auto_fixable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            threat.threat_id,
            threat.category.value,
            threat.severity.value,
            threat.title,
            threat.description,
            threat.affected_file,
            threat.affected_line,
            threat.cwe_id,
            threat.cvss_score,
            threat.remediation,
            threat.auto_fixable
        ))

        conn.commit()

    async def auto_remediate(self, threat: ThreatDetection) -> RemediationAction:
        """
        Attempt automated remediation of threat

        Args:
            threat: Threat to remediate

        Returns:
            Remediation action result
        """
        if not threat.auto_fixable:
            return RemediationAction(
                action_id=f"rem_{threat.threat_id}",
                threat_id=threat.threat_id,
                action_type="alert",
                description="Manual remediation required",
                applied=False,
                success=False,
                error_message="Threat not auto-fixable"
            )

        # Find appropriate agent
        agent_map = {
            ThreatCategory.CODE_INJECTION: "code_injection",
            ThreatCategory.AUTHENTICATION: "authentication",
            ThreatCategory.DATA_SECURITY: "data_protection",
            ThreatCategory.DEPENDENCY: "dependency",
        }

        agent_name = agent_map.get(threat.category)
        if not agent_name or agent_name not in self.agents:
            return RemediationAction(
                action_id=f"rem_{threat.threat_id}",
                threat_id=threat.threat_id,
                action_type="alert",
                description="No agent available",
                applied=False,
                success=False
            )

        agent = self.agents[agent_name]
        action = await agent.remediate(threat)

        # Store remediation
        conn = self.db.connect_workspace()
        conn.execute("""
            INSERT INTO security_remediations (
                action_id, threat_id, action_type, description,
                applied, success, error_message, applied_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            action.action_id,
            action.threat_id,
            action.action_type,
            action.description,
            action.applied,
            action.success,
            action.error_message
        ))

        # Update threat status if remediation succeeded
        if action.success:
            conn.execute("""
                UPDATE security_threats
                SET status = 'resolved',
                    resolved_at = CURRENT_TIMESTAMP
                WHERE threat_id = ?
            """, (threat.threat_id,))

        conn.commit()

        return action

    def get_security_dashboard(self) -> Dict[str, Any]:
        """
        Get current security status for dashboard

        Returns:
            Dashboard metrics and stats
        """
        conn = self.db.connect_workspace()

        # Open threats by severity
        cursor = conn.execute("""
            SELECT severity, COUNT(*) as count
            FROM security_threats
            WHERE status = 'open'
            GROUP BY severity
        """)
        threats_by_severity = {row[0]: row[1] for row in cursor.fetchall()}

        # Recent scans
        cursor = conn.execute("""
            SELECT scan_id, scan_type, threats_found, completed_at
            FROM security_scans
            WHERE status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 10
        """)
        recent_scans = [dict(row) for row in cursor.fetchall()]

        # Compliance status
        cursor = conn.execute("""
            SELECT framework,
                   SUM(CASE WHEN status = 'pass' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as compliance_percent
            FROM compliance_checks
            GROUP BY framework
        """)
        compliance_status = {row[0]: row[1] for row in cursor.fetchall()}

        # Metrics today
        cursor = conn.execute("""
            SELECT * FROM security_metrics
            WHERE metric_date = date('now')
        """)
        todays_metrics = dict(cursor.fetchone() or {})

        return {
            "threats_by_severity": threats_by_severity,
            "recent_scans": recent_scans,
            "compliance_status": compliance_status,
            "todays_metrics": todays_metrics,
            "active_agents": len(self.agents),
            "is_monitoring": self.is_monitoring
        }

    async def start_monitoring(self):
        """Start continuous security monitoring"""
        self.is_monitoring = True

        # Monitor in background
        asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            # Check for new threats
            # Update metrics
            # Send alerts

            await asyncio.sleep(60)  # Check every minute

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
