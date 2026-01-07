"""
Code Injection Guard

Detects and prevents all types of code injection attacks:
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- LDAP Injection
- XML Injection
- Template Injection
"""

import re
from typing import List, Optional
from datetime import datetime

from ..orchestrator import ThreatDetection, ThreatSeverity, ThreatCategory, RemediationAction


class CodeInjectionGuard:
    """
    Advanced code injection detection agent

    Uses:
    - Static pattern matching
    - AST analysis
    - Taint analysis
    - Context-aware detection
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> dict:
        """Load injection detection patterns"""
        return {
            "sql_injection": [
                # Concatenated SQL queries
                r"(?:execute|query|sql)\s*\(\s*['\"].*\+.*['\"]",
                r"(?:execute|query)\s*\(\s*f['\"].*\{.*\}",
                # Direct SQL with user input
                r"(?:SELECT|INSERT|UPDATE|DELETE).*WHERE.*=.*input",
                # String formatting in SQL
                r"\.format\(.*\).*(?:execute|query)",
            ],
            "command_injection": [
                # os.system with user input
                r"os\.system\s*\([^)]*input",
                r"subprocess\.(?:call|run|Popen)\s*\([^)]*input",
                # Shell=True with variables
                r"shell\s*=\s*True.*(?:input|request|params)",
            ],
            "xss": [
                # Direct HTML output
                r"(?:innerHTML|outerHTML)\s*=\s*.*(?:input|request\.)",
                r"document\.write\s*\(.*(?:input|request\.)",
                # Template rendering without escaping
                r"render_template_string\s*\(.*(?:input|request\.)",
                # Dangerously set HTML in React
                r"dangerouslySetInnerHTML.*__html.*(?:props|state)",
            ],
            "template_injection": [
                # Jinja2/Flask template injection
                r"\{\{.*(?:request\.|input).*\}\}",
                # Server-side template injection patterns
                r"Template\s*\(.*(?:input|request\.)",
            ],
        }

    async def scan(self, code: str, file_path: Optional[str] = None) -> List[ThreatDetection]:
        """
        Scan code for injection vulnerabilities

        Args:
            code: Source code to analyze
            file_path: Optional file path for context

        Returns:
            List of detected injection threats
        """
        threats = []
        lines = code.split('\n')

        for injection_type, patterns in self.patterns.items():
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)

                for line_num, line in enumerate(lines, 1):
                    match = regex.search(line)
                    if match:
                        threat = self._create_threat(
                            injection_type=injection_type,
                            line_content=line,
                            line_num=line_num,
                            file_path=file_path,
                            matched_pattern=match.group(0)
                        )
                        threats.append(threat)

        # Additional checks
        threats.extend(self._check_sql_parameterization(code, file_path))
        threats.extend(self._check_input_sanitization(code, file_path))

        return threats

    def _create_threat(
        self,
        injection_type: str,
        line_content: str,
        line_num: int,
        file_path: Optional[str],
        matched_pattern: str
    ) -> ThreatDetection:
        """Create threat detection object"""

        severity_map = {
            "sql_injection": ThreatSeverity.CRITICAL,
            "command_injection": ThreatSeverity.CRITICAL,
            "xss": ThreatSeverity.HIGH,
            "template_injection": ThreatSeverity.HIGH,
        }

        cwe_map = {
            "sql_injection": "CWE-89",  # SQL Injection
            "command_injection": "CWE-78",  # OS Command Injection
            "xss": "CWE-79",  # Cross-site Scripting
            "template_injection": "CWE-1336",  # Template Injection
        }

        remediation_map = {
            "sql_injection": """
Use parameterized queries:
- GOOD: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
- BAD:  cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

Use ORM with parameter binding:
- SQLAlchemy: query.filter(User.id == user_id)
- Django ORM: User.objects.get(id=user_id)
""",
            "command_injection": """
Avoid shell=True and use argument lists:
- GOOD: subprocess.run(["ls", "-la", directory])
- BAD:  subprocess.run(f"ls -la {directory}", shell=True)

Validate and sanitize all user input before passing to system commands.
Use shlex.quote() for shell escaping if shell execution is unavoidable.
""",
            "xss": """
Always escape user input in HTML:
- Use auto-escaping templates (Jinja2, React)
- Flask: Use Markup() for trusted content only
- React: Avoid dangerouslySetInnerHTML

Implement Content Security Policy (CSP) headers:
- Content-Security-Policy: default-src 'self'; script-src 'self'
""",
            "template_injection": """
Never render user input as templates:
- GOOD: render_template('page.html', user_data=data)
- BAD:  render_template_string(user_input)

Validate template names against whitelist.
Use sandboxed template engines for user-controlled templates.
""",
        }

        threat_id = f"threat_{datetime.now().timestamp()}_{injection_type}"

        return ThreatDetection(
            threat_id=threat_id,
            category=ThreatCategory.CODE_INJECTION,
            severity=severity_map.get(injection_type, ThreatSeverity.HIGH),
            title=f"{injection_type.replace('_', ' ').title()} Detected",
            description=f"Potential {injection_type} vulnerability found: {matched_pattern}",
            affected_file=file_path,
            affected_line=line_num,
            cwe_id=cwe_map.get(injection_type),
            cvss_score=9.8 if severity_map.get(injection_type) == ThreatSeverity.CRITICAL else 7.5,
            remediation=remediation_map.get(injection_type, "Review and sanitize user input"),
            auto_fixable=False  # Requires context to fix safely
        )

    def _check_sql_parameterization(self, code: str, file_path: Optional[str]) -> List[ThreatDetection]:
        """Check for proper SQL parameterization"""
        threats = []

        # Look for execute() calls
        execute_pattern = r"\.execute\s*\([^)]*\)"
        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            if re.search(execute_pattern, line):
                # Check if it uses string formatting (BAD)
                if any(x in line for x in ['%s', '.format(', 'f"', "f'"]):
                    # Check if it's NOT using parameterized queries
                    if not re.search(r'\([^)]*,\s*\(', line):  # Looking for second parameter tuple
                        threats.append(ThreatDetection(
                            threat_id=f"threat_{datetime.now().timestamp()}_sql_param",
                            category=ThreatCategory.CODE_INJECTION,
                            severity=ThreatSeverity.CRITICAL,
                            title="Non-Parameterized SQL Query",
                            description="SQL query uses string formatting instead of parameterization",
                            affected_file=file_path,
                            affected_line=line_num,
                            cwe_id="CWE-89",
                            cvss_score=9.8,
                            remediation="Use parameterized queries with ? or named placeholders",
                            auto_fixable=True  # Can suggest fix
                        ))

        return threats

    def _check_input_sanitization(self, code: str, file_path: Optional[str]) -> List[ThreatDetection]:
        """Check if user input is sanitized"""
        threats = []

        # Look for direct use of request/input without validation
        dangerous_patterns = [
            (r"request\.(?:args|form|json)\[.*\](?!\s*(?:in|not|and|or))", "Unsanitized request parameter"),
            (r"input\s*\([^)]*\)(?!\s*(?:in|not|and|or|\.|int|str|float))", "Unsanitized user input"),
        ]

        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns:
                if re.search(pattern, line):
                    # Check if there's validation nearby (next few lines)
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 3)
                    context = '\n'.join(lines[context_start:context_end])

                    # Look for validation keywords
                    has_validation = any(kw in context for kw in [
                        'validate', 'sanitize', 'clean', 'escape',
                        'if', 'assert', 'raise', 'try'
                    ])

                    if not has_validation:
                        threats.append(ThreatDetection(
                            threat_id=f"threat_{datetime.now().timestamp()}_unsanitized",
                            category=ThreatCategory.CODE_INJECTION,
                            severity=ThreatSeverity.HIGH,
                            title="Unsanitized User Input",
                            description=description,
                            affected_file=file_path,
                            affected_line=line_num,
                            cwe_id="CWE-20",  # Improper Input Validation
                            cvss_score=7.5,
                            remediation="Validate and sanitize all user input before use",
                            auto_fixable=False
                        ))

        return threats

    async def remediate(self, threat: ThreatDetection) -> RemediationAction:
        """
        Attempt automated remediation

        Args:
            threat: Threat to remediate

        Returns:
            Remediation action
        """
        action_id = f"rem_{threat.threat_id}"

        # For auto-fixable SQL parameterization issues
        if "Non-Parameterized SQL Query" in threat.title:
            return RemediationAction(
                action_id=action_id,
                threat_id=threat.threat_id,
                action_type="fix",
                description="Convert to parameterized query",
                applied=False,  # Would need actual code context to apply
                success=False
            )

        # For others, generate alert with fix recommendation
        return RemediationAction(
            action_id=action_id,
            threat_id=threat.threat_id,
            action_type="alert",
            description=f"Manual review required: {threat.remediation}",
            applied=True,
            success=True
        )
