"""Compliance rule data model."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

from .audit_event import AuditEvent, RiskFinding, RiskLevel


class RuleCategory(Enum):
    """Categories of compliance rules."""
    SECURITY = "security"
    PRIVACY = "privacy"
    ETHICS = "ethics"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    CUSTOM = "custom"


@dataclass
class ComplianceRule:
    """Defines a compliance rule for auditing AI Agent behavior."""

    rule_id: str
    name: str
    description: str
    category: RuleCategory
    risk_level: RiskLevel
    enabled: bool = True

    # Rule configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Custom check function (optional)
    custom_check: Optional[Callable[[AuditEvent, Dict[str, Any]], Optional[RiskFinding]]] = None

    def check(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check if the event violates this rule."""
        if not self.enabled:
            return None

        # If custom check is provided, use it
        if self.custom_check:
            return self.custom_check(event, self.config)

        # Otherwise, use built-in checks based on category
        return self._built_in_check(event)

    def _built_in_check(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Built-in rule checking logic."""
        check_methods = {
            "sensitive_data_exposure": self._check_sensitive_data,
            "excessive_token_usage": self._check_token_usage,
            "repeated_errors": self._check_repeated_errors,
            "unauthorized_tool_access": self._check_tool_access,
            "prompt_injection": self._check_prompt_injection,
            "hallucination_risk": self._check_hallucination,
            "bias_detection": self._check_bias,
            "response_latency": self._check_latency,
        }

        check_method = check_methods.get(self.rule_id)
        if check_method:
            return check_method(event)

        return None

    def _check_sensitive_data(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for sensitive data exposure."""
        sensitive_patterns = self.config.get("patterns", [
            r"\b\d{16}\b",  # Credit card
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",  # Email
            r"password\s*[=:]\s*\S+",  # Password patterns
            r"api[_-]?key\s*[=:]\s*\S+",  # API keys
        ])

        import re
        content = str(event.output_data)
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return RiskFinding(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    risk_level=self.risk_level,
                    message=f"Potential sensitive data detected in output",
                    details={"pattern_type": pattern},
                )
        return None

    def _check_token_usage(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for excessive token usage."""
        threshold = self.config.get("threshold", 4000)
        tokens = event.metadata.get("token_count", 0)
        if tokens > threshold:
            return RiskFinding(
                rule_id=self.rule_id,
                rule_name=self.name,
                risk_level=self.risk_level,
                message=f"High token usage detected: {tokens} tokens",
                details={"token_count": tokens, "threshold": threshold},
            )
        return None

    def _check_repeated_errors(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for repeated error patterns."""
        if event.event_type != "error":
            return None

        error_threshold = self.config.get("error_threshold", 3)
        window_size = self.config.get("window_size", 10)

        # This would need session history to properly implement
        # Simplified version for demonstration
        return None

    def _check_tool_access(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for unauthorized tool access."""
        if event.event_type != "tool_call":
            return None

        allowed_tools = self.config.get("allowed_tools", [])
        tool_name = event.metadata.get("tool_name", "")

        if allowed_tools and tool_name not in allowed_tools:
            return RiskFinding(
                rule_id=self.rule_id,
                rule_name=self.name,
                risk_level=self.risk_level,
                message=f"Unauthorized tool access: {tool_name}",
                details={"tool": tool_name, "allowed_tools": allowed_tools},
            )
        return None

    def _check_prompt_injection(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for potential prompt injection attempts."""
        injection_patterns = self.config.get("patterns", [
            r"ignore\s+(previous|above|earlier)",
            r"forget\s+(previous|above|earlier)",
            r"system\s*prompt",
            r"you\s+are\s+now",
            r"new\s+instructions",
            r"DAN\s*mode",
            r"jailbreak",
        ])

        import re
        content = str(event.input_data)
        for pattern in injection_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return RiskFinding(
                    rule_id=self.rule_id,
                    rule_name=self.name,
                    risk_level=self.risk_level,
                    message="Potential prompt injection attempt detected",
                    details={"matched_pattern": pattern},
                )
        return None

    def _check_hallucination(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for potential hallucination indicators."""
        hallucination_indicators = self.config.get("indicators", [
            "I believe", "I think", "probably", "maybe", "likely",
            "I'm not sure", "I don't know exactly", "approximately",
        ])

        content = str(event.output_data).lower()
        matches = [ind for ind in hallucination_indicators if ind.lower() in content]

        if len(matches) >= self.config.get("threshold", 3):
            return RiskFinding(
                rule_id=self.rule_id,
                rule_name=self.name,
                risk_level=self.risk_level,
                message=f"Potential hallucination indicators detected ({len(matches)} matches)",
                details={"indicators_found": matches},
            )
        return None

    def _check_bias(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for potential biased content."""
        # Simplified bias detection
        return None

    def _check_latency(self, event: AuditEvent) -> Optional[RiskFinding]:
        """Check for high response latency."""
        threshold_ms = self.config.get("threshold_ms", 5000)
        latency = event.metadata.get("latency_ms", 0)

        if latency > threshold_ms:
            return RiskFinding(
                rule_id=self.rule_id,
                rule_name=self.name,
                risk_level=self.risk_level,
                message=f"High response latency: {latency}ms",
                details={"latency_ms": latency, "threshold_ms": threshold_ms},
            )
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "risk_level": self.risk_level.value,
            "enabled": self.enabled,
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComplianceRule":
        """Create rule from dictionary."""
        return cls(
            rule_id=data["rule_id"],
            name=data["name"],
            description=data["description"],
            category=RuleCategory(data.get("category", "custom")),
            risk_level=RiskLevel(data.get("risk_level", "info")),
            enabled=data.get("enabled", True),
            config=data.get("config", {}),
        )
