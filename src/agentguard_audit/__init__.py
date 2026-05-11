"""
AgentGuard-Audit: AI Agent Runtime Behavior Compliance Audit Engine

A lightweight, zero-dependency runtime audit engine for AI Agent behavior compliance.
Provides real-time interception, multi-dimensional risk detection, and comprehensive
audit reporting for AI agents.

Author: Lobster Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Lobster Team"
__license__ = "MIT"

from .core.audit_engine import AuditEngine
from .core.interceptor import AgentInterceptor
from .core.risk_detector import RiskDetector
from .models.audit_event import AuditEvent, RiskLevel
from .models.compliance_rule import ComplianceRule
from .reporters.console_reporter import ConsoleReporter
from .reporters.html_reporter import HTMLReporter
from .reporters.json_reporter import JSONReporter

__all__ = [
    "AuditEngine",
    "AgentInterceptor",
    "RiskDetector",
    "AuditEvent",
    "RiskLevel",
    "ComplianceRule",
    "ConsoleReporter",
    "HTMLReporter",
    "JSONReporter",
]
