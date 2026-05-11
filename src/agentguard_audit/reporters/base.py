"""Base reporter interface."""

from abc import ABC, abstractmethod
from typing import Any

from ..models.audit_report import AuditReport


class BaseReporter(ABC):
    """Abstract base class for audit reporters."""

    @abstractmethod
    def generate(self, report: AuditReport) -> str:
        """Generate report output."""
        pass

    @abstractmethod
    def save(self, report: AuditReport, filepath: str) -> None:
        """Save report to file."""
        pass

    def _format_duration(self, start: Any, end: Any) -> str:
        """Format duration between two timestamps."""
        duration = (end - start).total_seconds()
        if duration < 60:
            return f"{duration:.1f}s"
        elif duration < 3600:
            return f"{duration/60:.1f}m"
        else:
            return f"{duration/3600:.1f}h"
