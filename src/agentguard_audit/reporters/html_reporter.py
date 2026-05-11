"""HTML reporter for web-viewable reports."""

from ..models.audit_report import AuditReport
from ..models.audit_event import RiskLevel
from .base import BaseReporter


class HTMLReporter(BaseReporter):
    """Generate interactive HTML audit reports."""

    def __init__(self, theme: str = "light"):
        """Initialize reporter."""
        self.theme = theme

    def _get_risk_color(self, level: RiskLevel) -> str:
        """Get color for risk level."""
        return level.color

    def generate(self, report: AuditReport) -> str:
        """Generate HTML report."""
        summary = report.summary

        # Build risk distribution chart
        risk_chart_data = []
        for level in RiskLevel:
            count = summary['risk_distribution'][level.value]
            if count > 0:
                risk_chart_data.append({
                    'label': level.value.upper(),
                    'value': count,
                    'color': self._get_risk_color(level),
                })

        # Build risk items HTML
        risk_items_html = ""
        for item in risk_chart_data:
            bar_width = min(item['value'] * 10, 100)
            risk_items_html += f"""
                <div class="risk-item">
                    <span class="badge" style="background: {item['color']}">{item['label']}</span>
                    <span>{item['value']}</span>
                    <div class="risk-bar">
                        <div class="risk-bar-fill" style="width: {bar_width}%; background: {item['color']}"></div>
                    </div>
                </div>
            """

        # Build events table
        events_rows = []
        for event in report.events:
            findings_html = ""
            for finding in event.findings:
                findings_html += f"""
                <div class="finding">
                    <span class="badge" style="background: {finding.risk_level.color}">{finding.risk_level.value}</span>
                    <span class="finding-message">{finding.message}</span>
                </div>
                """

            events_rows.append(f"""
            <tr class="risk-{event.risk_level.value}">
                <td>{event.timestamp.strftime('%H:%M:%S')}</td>
                <td>{event.event_type}</td>
                <td><span class="badge" style="background: {event.risk_level.color}">{event.risk_level.value}</span></td>
                <td>{event.risk_score}</td>
                <td>{findings_html or '<em>No findings</em>'}</td>
            </tr>
            """)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentGuard Audit Report - {report.agent_name}</title>
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
        }}

        header h1 {{
            font-size: 1.875rem;
            margin-bottom: 0.5rem;
        }}

        header p {{
            opacity: 0.9;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .card {{
            background: var(--bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }}

        .card h3 {{
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}

        .card .value {{
            font-size: 2rem;
            font-weight: 700;
        }}

        .compliance-score {{
            color: {'#16A34A' if summary['compliance_score'] >= 80 else '#CA8A04' if summary['compliance_score'] >= 60 else '#DC2626'};
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
        }}

        .section {{
            background: var(--bg-primary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }}

        .section h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}

        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}

        tr:hover {{
            background: var(--bg-tertiary);
        }}

        .finding {{
            margin: 0.25rem 0;
            padding: 0.5rem;
            background: var(--bg-secondary);
            border-radius: 6px;
        }}

        .finding-message {{
            margin-left: 0.5rem;
            color: var(--text-secondary);
        }}

        .risk-distribution {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .risk-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .risk-bar {{
            width: 100px;
            height: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            overflow: hidden;
        }}

        .risk-bar-fill {{
            height: 100%;
            border-radius: 4px;
        }}

        footer {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ AgentGuard Audit Report</h1>
            <p>{report.agent_name} • Session {report.session_id[:8]}...</p>
        </header>

        <div class="grid">
            <div class="card">
                <h3>Total Events</h3>
                <div class="value">{summary['total_events']}</div>
            </div>
            <div class="card">
                <h3>Compliance Score</h3>
                <div class="value compliance-score">{summary['compliance_score']}%</div>
            </div>
            <div class="card">
                <h3>Average Risk Score</h3>
                <div class="value">{summary['average_risk_score']}</div>
            </div>
            <div class="card">
                <h3>Total Findings</h3>
                <div class="value">{summary['total_findings']}</div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Risk Distribution</h2>
            <div class="risk-distribution">
                {risk_items_html}
            </div>
        </div>

        <div class="section">
            <h2>📋 Audit Events</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Event Type</th>
                        <th>Risk Level</th>
                        <th>Score</th>
                        <th>Findings</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(events_rows)}
                </tbody>
            </table>
        </div>

        <footer>
            <p>Generated by AgentGuard-Audit v1.0.0 • {report.end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </footer>
    </div>
</body>
</html>"""

        return html

    def save(self, report: AuditReport, filepath: str) -> None:
        """Save HTML report to file."""
        content = self.generate(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
