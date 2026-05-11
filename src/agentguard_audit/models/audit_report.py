"""Audit report data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from .audit_event import AuditEvent, RiskLevel


@dataclass
class AuditReport:
    """Comprehensive audit report for AI Agent sessions."""

    report_id: str
    start_time: datetime
    end_time: datetime
    agent_id: str
    agent_name: str
    session_id: str

    events: List[AuditEvent] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate summary after initialization."""
        if not self.summary:
            self._generate_summary()

    def _generate_summary(self) -> None:
        """Generate report summary statistics."""
        if not self.events:
            self.summary = {
                "total_events": 0,
                "risk_distribution": {level.value: 0 for level in RiskLevel},
                "average_risk_score": 0,
                "compliance_score": 100,
                "top_findings": [],
            }
            return

        total_events = len(self.events)
        risk_distribution = {level.value: 0 for level in RiskLevel}
        total_score = 0
        all_findings = []

        for event in self.events:
            risk_distribution[event.risk_level.value] += 1
            total_score += event.risk_score
            all_findings.extend(event.findings)

        avg_risk_score = total_score / total_events

        # Calculate compliance score (inverse of risk)
        critical_count = risk_distribution[RiskLevel.CRITICAL.value]
        high_count = risk_distribution[RiskLevel.HIGH.value]
        medium_count = risk_distribution[RiskLevel.MEDIUM.value]

        compliance_score = max(0, 100 - (critical_count * 20 + high_count * 10 + medium_count * 5))

        # Top findings by severity
        sorted_findings = sorted(
            all_findings,
            key=lambda f: f.risk_level.score,
            reverse=True
        )[:10]

        self.summary = {
            "total_events": total_events,
            "risk_distribution": risk_distribution,
            "average_risk_score": round(avg_risk_score, 2),
            "compliance_score": compliance_score,
            "total_findings": len(all_findings),
            "top_findings": [
                {
                    "rule_name": f.rule_name,
                    "risk_level": f.risk_level.value,
                    "message": f.message,
                }
                for f in sorted_findings
            ],
        }

    def get_events_by_risk(self, risk_level: RiskLevel) -> List[AuditEvent]:
        """Get all events with specified risk level."""
        return [e for e in self.events if e.risk_level == risk_level]

    def get_high_risk_events(self) -> List[AuditEvent]:
        """Get all high and critical risk events."""
        return [e for e in self.events if e.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_id": self.report_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "events": [e.to_dict() for e in self.events],
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditReport":
        """Create report from dictionary."""
        events = [AuditEvent.from_dict(e) for e in data.get("events", [])]
        return cls(
            report_id=data["report_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            session_id=data["session_id"],
            events=events,
            summary=data.get("summary", {}),
        )
