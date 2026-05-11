"""Audit event data model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def score(self) -> int:
        """Get numeric score for risk level."""
        scores = {
            RiskLevel.CRITICAL: 100,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25,
            RiskLevel.INFO: 0,
        }
        return scores.get(self, 0)

    @property
    def color(self) -> str:
        """Get color code for risk level."""
        colors = {
            RiskLevel.CRITICAL: "#DC2626",
            RiskLevel.HIGH: "#EA580C",
            RiskLevel.MEDIUM: "#CA8A04",
            RiskLevel.LOW: "#16A34A",
            RiskLevel.INFO: "#2563EB",
        }
        return colors.get(self, "#6B7280")


@dataclass
class RiskFinding:
    """Individual risk finding within an audit event."""
    rule_id: str
    rule_name: str
    risk_level: RiskLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    """Represents a single auditable event in an AI Agent's lifecycle."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent_id: str = ""
    agent_name: str = ""
    event_type: str = ""  # e.g., "tool_call", "llm_request", "response", "error"

    # Event content
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Risk assessment
    risk_level: RiskLevel = RiskLevel.INFO
    risk_score: int = 0
    findings: List[RiskFinding] = field(default_factory=list)

    # Context
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    parent_event_id: Optional[str] = None

    def add_finding(self, finding: RiskFinding) -> None:
        """Add a risk finding and update overall risk level."""
        self.findings.append(finding)
        # Update overall risk level to the highest severity
        if finding.risk_level.score > self.risk_level.score:
            self.risk_level = finding.risk_level
        self._recalculate_score()

    def _recalculate_score(self) -> None:
        """Recalculate overall risk score based on findings."""
        if not self.findings:
            self.risk_score = 0
            return
        # Weighted sum of findings
        total_score = sum(f.risk_level.score for f in self.findings)
        # Apply multiplier for multiple findings
        multiplier = 1 + (len(self.findings) - 1) * 0.1
        self.risk_score = min(int(total_score * multiplier / len(self.findings)), 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "event_type": self.event_type,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "metadata": self.metadata,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "rule_name": f.rule_name,
                    "risk_level": f.risk_level.value,
                    "message": f.message,
                    "details": f.details,
                }
                for f in self.findings
            ],
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "parent_event_id": self.parent_event_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Create event from dictionary."""
        event = cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow(),
            agent_id=data.get("agent_id", ""),
            agent_name=data.get("agent_name", ""),
            event_type=data.get("event_type", ""),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            metadata=data.get("metadata", {}),
            risk_level=RiskLevel(data.get("risk_level", "info")),
            risk_score=data.get("risk_score", 0),
            session_id=data.get("session_id"),
            conversation_id=data.get("conversation_id"),
            parent_event_id=data.get("parent_event_id"),
        )
        for f_data in data.get("findings", []):
            finding = RiskFinding(
                rule_id=f_data["rule_id"],
                rule_name=f_data["rule_name"],
                risk_level=RiskLevel(f_data["risk_level"]),
                message=f_data["message"],
                details=f_data.get("details", {}),
            )
            event.findings.append(finding)
        return event
