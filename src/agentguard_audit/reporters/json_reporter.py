"""JSON reporter for machine-readable output."""

import json
from datetime import datetime
from typing import Any

from ..models.audit_report import AuditReport
from .base import BaseReporter


class JSONReporter(BaseReporter):
    """Generate JSON format audit reports."""

    def __init__(self, indent: int = 2):
        """Initialize reporter."""
        self.indent = indent

    def _serialize_datetime(self, obj: Any) -> str:
        """Serialize datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def generate(self, report: AuditReport) -> str:
        """Generate JSON report."""
        data = report.to_dict()
        return json.dumps(data, indent=self.indent, default=self._serialize_datetime)

    def save(self, report: AuditReport, filepath: str) -> None:
        """Save JSON report to file."""
        content = self.generate(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
