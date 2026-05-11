"""Console reporter for terminal output."""

from typing import Any

from ..models.audit_report import AuditReport
from ..models.audit_event import RiskLevel
from .base import BaseReporter


class ConsoleReporter(BaseReporter):
    """Generate human-readable console output."""

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "critical": "\033[91m",  # Red
        "high": "\033[93m",      # Yellow
        "medium": "\033[94m",    # Blue
        "low": "\033[92m",       # Green
        "info": "\033[90m",      # Gray
        "header": "\033[95m",    # Magenta
    }

    def __init__(self, use_colors: bool = True):
        """Initialize reporter."""
        self.use_colors = use_colors

    def _color(self, text: str, color: str) -> str:
        """Apply color to text."""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _risk_badge(self, level: RiskLevel) -> str:
        """Create risk level badge."""
        color_map = {
            RiskLevel.CRITICAL: "critical",
            RiskLevel.HIGH: "high",
            RiskLevel.MEDIUM: "medium",
            RiskLevel.LOW: "low",
            RiskLevel.INFO: "info",
        }
        return self._color(f"[{level.value.upper()}]", color_map.get(level, "info"))

    def generate(self, report: AuditReport) -> str:
        """Generate console report."""
        lines = []

        # Header
        lines.append("")
        lines.append(self._color("=" * 70, "header"))
        lines.append(self._color("  AGENTGUARD AUDIT REPORT", "header"))
        lines.append(self._color("=" * 70, "header"))
        lines.append("")

        # Session Info
        lines.append(self._color("📋 SESSION INFORMATION", "bold"))
        lines.append(f"  Agent:        {report.agent_name} ({report.agent_id})")
        lines.append(f"  Session ID:   {report.session_id}")
        lines.append(f"  Report ID:    {report.report_id}")
        lines.append(f"  Duration:     {self._format_duration(report.start_time, report.end_time)}")
        lines.append(f"  Generated:    {report.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")

        # Summary
        summary = report.summary
        lines.append(self._color("📊 SUMMARY", "bold"))
        lines.append(f"  Total Events:      {summary['total_events']}")
        lines.append(f"  Total Findings:    {summary['total_findings']}")
        lines.append(f"  Compliance Score:  {summary['compliance_score']}%")
        lines.append(f"  Avg Risk Score:    {summary['average_risk_score']}")
        lines.append("")

        # Risk Distribution
        lines.append(self._color("🎯 RISK DISTRIBUTION", "bold"))
        for level in RiskLevel:
            count = summary['risk_distribution'][level.value]
            if count > 0:
                bar = "█" * min(count, 50)
                lines.append(f"  {self._risk_badge(level)} {count:4d} {bar}")
        lines.append("")

        # High Risk Events
        high_risk = report.get_high_risk_events()
        if high_risk:
            lines.append(self._color("⚠️  HIGH RISK EVENTS", "bold"))
            for event in high_risk[:10]:  # Show first 10
                lines.append(f"  {self._risk_badge(event.risk_level)} {event.event_type:15s} {event.timestamp.strftime('%H:%M:%S')}")
                for finding in event.findings:
                    lines.append(f"      → {finding.message[:60]}...")
            if len(high_risk) > 10:
                lines.append(f"      ... and {len(high_risk) - 10} more")
            lines.append("")

        # Top Findings
        if summary['top_findings']:
            lines.append(self._color("🔍 TOP FINDINGS", "bold"))
            for finding in summary['top_findings'][:5]:
                level = RiskLevel(finding['risk_level'])
                lines.append(f"  {self._risk_badge(level)} {finding['rule_name']}")
                lines.append(f"      {finding['message'][:70]}")
            lines.append("")

        # Footer
        lines.append(self._color("=" * 70, "header"))
        lines.append("")

        return "\n".join(lines)

    def save(self, report: AuditReport, filepath: str) -> None:
        """Save report to file."""
        content = self.generate(report)
        # Strip ANSI codes for file output
        import re
        clean_content = re.sub(r'\033\[[0-9;]*m', '', content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(clean_content)
