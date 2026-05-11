"""Rule engine for compliance checking."""

from typing import List

from ..models.audit_event import AuditEvent, RiskFinding
from ..models.compliance_rule import ComplianceRule


class RuleEngine:
    """Engine for managing and applying compliance rules."""

    def __init__(self):
        """Initialize rule engine with default rules."""
        self.rules: List[ComplianceRule] = []
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load built-in compliance rules."""
        from ..models.compliance_rule import RuleCategory
        from ..models.audit_event import RiskLevel

        default_rules = [
            ComplianceRule(
                rule_id="sensitive_data_exposure",
                name="Sensitive Data Exposure",
                description="Detects potential exposure of sensitive data like PII, credentials",
                category=RuleCategory.SECURITY,
                risk_level=RiskLevel.HIGH,
                config={},
            ),
            ComplianceRule(
                rule_id="excessive_token_usage",
                name="Excessive Token Usage",
                description="Detects unusually high token consumption",
                category=RuleCategory.PERFORMANCE,
                risk_level=RiskLevel.MEDIUM,
                config={"threshold": 4000},
            ),
            ComplianceRule(
                rule_id="unauthorized_tool_access",
                name="Unauthorized Tool Access",
                description="Detects access to tools not in allowed list",
                category=RuleCategory.SECURITY,
                risk_level=RiskLevel.CRITICAL,
                config={"allowed_tools": []},
            ),
            ComplianceRule(
                rule_id="prompt_injection",
                name="Prompt Injection Attempt",
                description="Detects potential prompt injection attacks",
                category=RuleCategory.SECURITY,
                risk_level=RiskLevel.CRITICAL,
                config={},
            ),
            ComplianceRule(
                rule_id="hallucination_risk",
                name="Hallucination Risk",
                description="Detects indicators of potential hallucination",
                category=RuleCategory.RELIABILITY,
                risk_level=RiskLevel.MEDIUM,
                config={"threshold": 3},
            ),
            ComplianceRule(
                rule_id="response_latency",
                name="High Response Latency",
                description="Detects slow responses that may indicate issues",
                category=RuleCategory.PERFORMANCE,
                risk_level=RiskLevel.LOW,
                config={"threshold_ms": 5000},
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule."""
        # Remove existing rule with same ID
        self.remove_rule(rule.rule_id)
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> None:
        """Remove a compliance rule by ID."""
        self.rules = [r for r in self.rules if r.rule_id != rule_id]

    def get_rule(self, rule_id: str) -> ComplianceRule:
        """Get a rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise KeyError(f"Rule not found: {rule_id}")

    def list_rules(self, enabled_only: bool = False) -> List[ComplianceRule]:
        """List all rules."""
        if enabled_only:
            return [r for r in self.rules if r.enabled]
        return self.rules.copy()

    def check_event(self, event: AuditEvent) -> List[RiskFinding]:
        """Check an event against all enabled rules."""
        findings = []
        for rule in self.rules:
            if not rule.enabled:
                continue
            finding = rule.check(event)
            if finding:
                findings.append(finding)
        return findings

    def enable_rule(self, rule_id: str) -> None:
        """Enable a rule."""
        rule = self.get_rule(rule_id)
        rule.enabled = True

    def disable_rule(self, rule_id: str) -> None:
        """Disable a rule."""
        rule = self.get_rule(rule_id)
        rule.enabled = False

    def update_rule_config(self, rule_id: str, config: dict) -> None:
        """Update a rule's configuration."""
        rule = self.get_rule(rule_id)
        rule.config.update(config)
