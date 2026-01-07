"""
Security Agent System for Unified AI Workspace

Comprehensive cybersecurity protection with 12 specialized agents:
- CodeInjectionGuard: Prevents injection attacks
- AuthenticationShield: Protects authentication systems
- DataProtectionAgent: Encrypts and secures data
- NetworkDefender: API and network security
- LogicGuardian: Business logic protection
- DependencyScanner: Vulnerable dependency detection
- InfrastructureAuditor: Cloud/container security
- AISecurityGuard: LLM-specific protections
- HumanFactorAnalyzer: Social engineering detection
- MobileSecurityAgent: Mobile app security
- WebSecurityAgent: Web application security
- ComplianceOfficer: Regulatory compliance
"""

from .orchestrator import SecurityOrchestrator
from .agents.code_injection_guard import CodeInjectionGuard
from .agents.authentication_shield import AuthenticationShield
from .agents.data_protection_agent import DataProtectionAgent
from .agents.dependency_scanner import DependencyScanner

__all__ = [
    "SecurityOrchestrator",
    "CodeInjectionGuard",
    "AuthenticationShield",
    "DataProtectionAgent",
    "DependencyScanner",
]
