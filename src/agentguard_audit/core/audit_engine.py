"""Main audit engine implementation."""

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from ..models.audit_event import AuditEvent, RiskFinding, RiskLevel
from ..models.audit_report import AuditReport
from ..models.compliance_rule import ComplianceRule
from .risk_detector import RiskDetector
from .rule_engine import RuleEngine


class AuditEngine:
    """
    Main audit engine for AI Agent behavior compliance monitoring.

    Provides real-time event auditing, risk detection, and comprehensive
    reporting capabilities.
    """

    def __init__(
        self,
        agent_id: str,
        agent_name: str = "",
        session_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the audit engine.

        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
            session_id: Optional session identifier
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.agent_name = agent_name or agent_id
        self.session_id = session_id or str(uuid.uuid4())
        self.config = config or {}

        # Initialize components
        self.rule_engine = RuleEngine()
        self.risk_detector = RiskDetector()

        # Event storage
        self.events: List[AuditEvent] = []
        self.start_time = datetime.utcnow()
        self._enabled = True

        # Callbacks
        self._on_risk_detected: Optional[Callable[[AuditEvent], None]] = None
        self._on_event_audited: Optional[Callable[[AuditEvent], None]] = None

    def enable(self) -> None:
        """Enable auditing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable auditing."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if auditing is enabled."""
        return self._enabled

    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule."""
        self.rule_engine.add_rule(rule)

    def remove_rule(self, rule_id: str) -> None:
        """Remove a compliance rule."""
        self.rule_engine.remove_rule(rule_id)

    def set_risk_callback(self, callback: Callable[[AuditEvent], None]) -> None:
        """Set callback for when risk is detected."""
        self._on_risk_detected = callback

    def set_event_callback(self, callback: Callable[[AuditEvent], None]) -> None:
        """Set callback for when event is audited."""
        self._on_event_audited = callback

    def audit_event(
        self,
        event_type: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_event_id: Optional[str] = None,
    ) -> AuditEvent:
        """
        Audit a single agent event.

        Args:
            event_type: Type of event (e.g., "tool_call", "llm_request")
            input_data: Input data for the event
            output_data: Optional output data
            metadata: Optional metadata
            parent_event_id: Optional parent event ID for tracing

        Returns:
            The audited event with risk assessment
        """
        if not self._enabled:
            # Create event without auditing
            return AuditEvent(
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                event_type=event_type,
                input_data=input_data,
                output_data=output_data or {},
                metadata=metadata or {},
                session_id=self.session_id,
                parent_event_id=parent_event_id,
            )

        # Create event
        event = AuditEvent(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            event_type=event_type,
            input_data=input_data,
            output_data=output_data or {},
            metadata=metadata or {},
            session_id=self.session_id,
            parent_event_id=parent_event_id,
        )

        # Run compliance checks
        findings = self.rule_engine.check_event(event)
        for finding in findings:
            event.add_finding(finding)

        # Additional risk detection
        risk_findings = self.risk_detector.detect(event)
        for finding in risk_findings:
            event.add_finding(finding)

        # Store event
        self.events.append(event)

        # Trigger callbacks
        if self._on_event_audited:
            self._on_event_audited(event)

        if event.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) and self._on_risk_detected:
            self._on_risk_detected(event)

        return event

    def audit_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Optional[Any] = None,
        latency_ms: Optional[float] = None,
    ) -> AuditEvent:
        """Convenience method to audit a tool call."""
        metadata = {"tool_name": tool_name}
        if latency_ms is not None:
            metadata["latency_ms"] = latency_ms

        return self.audit_event(
            event_type="tool_call",
            input_data={"tool": tool_name, "arguments": tool_input},
            output_data={"result": tool_output} if tool_output is not None else {},
            metadata=metadata,
        )

    def audit_llm_request(
        self,
        prompt: str,
        response: Optional[str] = None,
        token_count: Optional[int] = None,
        latency_ms: Optional[float] = None,
    ) -> AuditEvent:
        """Convenience method to audit an LLM request."""
        metadata = {}
        if token_count is not None:
            metadata["token_count"] = token_count
        if latency_ms is not None:
            metadata["latency_ms"] = latency_ms

        return self.audit_event(
            event_type="llm_request",
            input_data={"prompt": prompt},
            output_data={"response": response} if response else {},
            metadata=metadata,
        )

    def audit_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Convenience method to audit an error."""
        return self.audit_event(
            event_type="error",
            input_data=context or {},
            output_data={"error_type": error_type, "error_message": error_message},
            metadata={"error": True},
        )

    def generate_report(self) -> AuditReport:
        """Generate comprehensive audit report."""
        return AuditReport(
            report_id=str(uuid.uuid4()),
            start_time=self.start_time,
            end_time=datetime.utcnow(),
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            session_id=self.session_id,
            events=self.events.copy(),
        )

    def get_events(
        self,
        event_type: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
    ) -> List[AuditEvent]:
        """Get filtered events."""
        events = self.events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]

        return events

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get quick risk summary."""
        if not self.events:
            return {
                "total_events": 0,
                "high_risk_events": 0,
                "compliance_score": 100,
            }

        high_risk = len([e for e in self.events if e.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)])
        total = len(self.events)

        return {
            "total_events": total,
            "high_risk_events": high_risk,
            "compliance_score": max(0, 100 - (high_risk / total * 100)) if total > 0 else 100,
        }

    def clear_events(self) -> None:
        """Clear all stored events."""
        self.events.clear()
        self.start_time = datetime.utcnow()
