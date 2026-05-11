"""Tests for AuditEngine."""

import unittest
from datetime import datetime

from agentguard_audit.core.audit_engine import AuditEngine
from agentguard_audit.models.audit_event import RiskLevel
from agentguard_audit.models.compliance_rule import ComplianceRule, RuleCategory


class TestAuditEngine(unittest.TestCase):
    """Test cases for AuditEngine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = AuditEngine(
            agent_id="test-agent",
            agent_name="Test Agent",
        )

    def test_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.agent_id, "test-agent")
        self.assertEqual(self.engine.agent_name, "Test Agent")
        self.assertTrue(self.engine.is_enabled)
        self.assertEqual(len(self.engine.events), 0)

    def test_enable_disable(self):
        """Test enable/disable functionality."""
        self.engine.disable()
        self.assertFalse(self.engine.is_enabled)

        self.engine.enable()
        self.assertTrue(self.engine.is_enabled)

    def test_audit_event(self):
        """Test basic event auditing."""
        event = self.engine.audit_event(
            event_type="test",
            input_data={"key": "value"},
            output_data={"result": "success"},
        )

        self.assertEqual(event.event_type, "test")
        self.assertEqual(event.agent_id, "test-agent")
        self.assertEqual(len(self.engine.events), 1)

    def test_audit_tool_call(self):
        """Test tool call auditing."""
        event = self.engine.audit_tool_call(
            tool_name="test_tool",
            tool_input={"arg": "value"},
            tool_output={"status": "ok"},
            latency_ms=100,
        )

        self.assertEqual(event.event_type, "tool_call")
        self.assertEqual(event.metadata.get("tool_name"), "test_tool")
        self.assertEqual(event.metadata.get("latency_ms"), 100)

    def test_audit_llm_request(self):
        """Test LLM request auditing."""
        event = self.engine.audit_llm_request(
            prompt="Hello",
            response="Hi there",
            token_count=150,
            latency_ms=500,
        )

        self.assertEqual(event.event_type, "llm_request")
        self.assertEqual(event.metadata.get("token_count"), 150)

    def test_audit_error(self):
        """Test error auditing."""
        event = self.engine.audit_error(
            error_type="TestError",
            error_message="Something went wrong",
        )

        self.assertEqual(event.event_type, "error")
        self.assertEqual(event.output_data.get("error_type"), "TestError")

    def test_add_rule(self):
        """Test adding custom rules."""
        rule = ComplianceRule(
            rule_id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.CUSTOM,
            risk_level=RiskLevel.MEDIUM,
        )

        self.engine.add_rule(rule)
        retrieved = self.engine.rule_engine.get_rule("test_rule")
        self.assertEqual(retrieved.name, "Test Rule")

    def test_generate_report(self):
        """Test report generation."""
        # Create some events
        self.engine.audit_event("test1", {}, {})
        self.engine.audit_event("test2", {}, {})

        report = self.engine.generate_report()

        self.assertEqual(report.agent_id, "test-agent")
        self.assertEqual(len(report.events), 2)
        self.assertIn("total_events", report.summary)

    def test_get_events_filtering(self):
        """Test event filtering."""
        self.engine.audit_event("type_a", {}, {})
        self.engine.audit_event("type_b", {}, {})
        self.engine.audit_event("type_a", {}, {})

        type_a_events = self.engine.get_events(event_type="type_a")
        self.assertEqual(len(type_a_events), 2)

    def test_clear_events(self):
        """Test clearing events."""
        self.engine.audit_event("test", {}, {})
        self.assertEqual(len(self.engine.events), 1)

        self.engine.clear_events()
        self.assertEqual(len(self.engine.events), 0)

    def test_risk_summary(self):
        """Test risk summary generation."""
        summary = self.engine.get_risk_summary()

        self.assertIn("total_events", summary)
        self.assertIn("high_risk_events", summary)
        self.assertIn("compliance_score", summary)


if __name__ == "__main__":
    unittest.main()
