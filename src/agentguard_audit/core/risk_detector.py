"""Advanced risk detection capabilities."""

import re
from typing import Dict, List, Optional

from ..models.audit_event import AuditEvent, RiskFinding, RiskLevel


class RiskDetector:
    """
    Advanced risk detector for AI Agent behavior analysis.

    Provides heuristic and pattern-based risk detection beyond rule-based checks.
    """

    def __init__(self):
        """Initialize risk detector."""
        self._sensitive_patterns = {
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "api_key": r"[a-zA-Z0-9]{32,}",
            "password": r"password\s*[=:]\s*[^\s]+",
            "secret": r"secret[_-]?key\s*[=:]\s*[^\s]+",
            "token": r"token\s*[=:]\s*[^\s]+",
        }

        self._injection_patterns = {
            "ignore_previous": r"ignore\s+(previous|above|earlier|all)\s+(instructions|prompts|commands)",
            "forget": r"forget\s+(everything|all|previous|above)",
            "system_prompt_leak": r"system\s*prompt|initial\s*instructions",
            "role_change": r"you\s+are\s+now|from\s+now\s+on\s+you\s+are",
            "jailbreak": r"DAN\s*mode|jailbreak|developer\s*mode",
            "delimiter": r"```\s*system|```\s*instructions",
        }

        self._hallucination_indicators = [
            "i believe", "i think", "probably", "maybe", "likely",
            "i'm not sure", "i don't know exactly", "approximately",
            "could be", "might be", "seems to be", "appears to be",
            "as far as i know", "to my knowledge", "if i recall correctly",
        ]

        self._repetition_threshold = 3

    def detect(self, event: AuditEvent) -> List[RiskFinding]:
        """
        Detect risks in an event using advanced heuristics.

        Args:
            event: The audit event to analyze

        Returns:
            List of risk findings
        """
        findings = []

        # Run various detection methods
        findings.extend(self._detect_sensitive_data(event))
        findings.extend(self._detect_injection_attempts(event))
        findings.extend(self._detect_hallucination_patterns(event))
        findings.extend(self._detect_repetition(event))
        findings.extend(self._detect_anomalies(event))

        return findings

    def _detect_sensitive_data(self, event: AuditEvent) -> List[RiskFinding]:
        """Detect sensitive data exposure."""
        findings = []
        content = str(event.output_data)

        for data_type, pattern in self._sensitive_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            match_list = list(matches)

            if match_list:
                # Mask the actual values in the finding
                masked_samples = []
                for m in match_list[:3]:  # Limit to first 3 matches
                    value = m.group()
                    masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
                    masked_samples.append(masked)

                findings.append(RiskFinding(
                    rule_id=f"heuristic_{data_type}",
                    rule_name=f"Potential {data_type.replace('_', ' ').title()} Exposure",
                    risk_level=RiskLevel.HIGH,
                    message=f"Detected potential {data_type.replace('_', ' ')} in output ({len(match_list)} occurrences)",
                    details={
                        "data_type": data_type,
                        "occurrence_count": len(match_list),
                        "samples": masked_samples,
                    }
                ))

        return findings

    def _detect_injection_attempts(self, event: AuditEvent) -> List[RiskFinding]:
        """Detect prompt injection attempts."""
        findings = []
        content = str(event.input_data).lower()

        detected_patterns = []
        for pattern_name, pattern in self._injection_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_patterns.append(pattern_name)

        if detected_patterns:
            risk_level = RiskLevel.CRITICAL if len(detected_patterns) >= 2 else RiskLevel.HIGH
            findings.append(RiskFinding(
                rule_id="heuristic_injection",
                rule_name="Advanced Injection Detection",
                risk_level=risk_level,
                message=f"Potential prompt injection attempt detected ({len(detected_patterns)} indicators)",
                details={"detected_patterns": detected_patterns},
            ))

        return findings

    def _detect_hallucination_patterns(self, event: AuditEvent) -> List[RiskFinding]:
        """Detect patterns indicating potential hallucination."""
        findings = []
        content = str(event.output_data).lower()

        # Count uncertainty indicators
        indicator_count = sum(1 for indicator in self._hallucination_indicators if indicator in content)

        # Check for contradictory statements
        contradictions = self._check_contradictions(content)

        if indicator_count >= 2 or contradictions:
            details = {
                "uncertainty_indicators": indicator_count,
                "contradictions_found": contradictions,
            }

            risk_level = RiskLevel.MEDIUM if indicator_count >= 3 else RiskLevel.LOW

            findings.append(RiskFinding(
                rule_id="heuristic_hallucination",
                rule_name="Hallucination Pattern Detection",
                risk_level=risk_level,
                message=f"Output contains indicators of potential hallucination",
                details=details,
            ))

        return findings

    def _check_contradictions(self, content: str) -> List[str]:
        """Check for contradictory statements in content."""
        contradictions = []

        # Simple contradiction patterns
        contradiction_pairs = [
            ("is", "is not"),
            ("was", "was not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("always", "never"),
            ("all", "none"),
        ]

        for pos, neg in contradiction_pairs:
            if pos in content and neg in content:
                contradictions.append(f"{pos}/{neg}")

        return contradictions

    def _detect_repetition(self, event: AuditEvent) -> List[RiskFinding]:
        """Detect repetitive patterns that might indicate issues."""
        findings = []
        content = str(event.output_data)

        # Check for repeated phrases
        words = content.lower().split()
        if len(words) >= 10:
            for i in range(len(words) - 5):
                phrase = " ".join(words[i:i+5])
                count = content.lower().count(phrase)
                if count >= self._repetition_threshold:
                    findings.append(RiskFinding(
                        rule_id="heuristic_repetition",
                        rule_name="Repetitive Output Detection",
                        risk_level=RiskLevel.LOW,
                        message="Output contains repetitive patterns",
                        details={
                            "repeated_phrase": phrase[:50] + "..." if len(phrase) > 50 else phrase,
                            "repetition_count": count,
                        },
                    ))
                    break  # Only report once per event

        return findings

    def _detect_anomalies(self, event: AuditEvent) -> List[RiskFinding]:
        """Detect anomalous behavior patterns."""
        findings = []

        # Check for unusually long outputs
        output_str = str(event.output_data)
        if len(output_str) > 10000:
            findings.append(RiskFinding(
                rule_id="heuristic_long_output",
                rule_name="Unusually Long Output",
                risk_level=RiskLevel.INFO,
                message=f"Output length ({len(output_str)} chars) exceeds typical range",
                details={"output_length": len(output_str)},
            ))

        # Check for empty or near-empty outputs
        if len(output_str.strip()) < 10:
            findings.append(RiskFinding(
                rule_id="heuristic_empty_output",
                rule_name="Empty or Minimal Output",
                risk_level=RiskLevel.MEDIUM,
                message="Output is empty or significantly shorter than expected",
                details={"output_length": len(output_str)},
            ))

        return findings

    def update_patterns(self, pattern_type: str, patterns: Dict[str, str]) -> None:
        """Update detection patterns."""
        if pattern_type == "sensitive":
            self._sensitive_patterns.update(patterns)
        elif pattern_type == "injection":
            self._injection_patterns.update(patterns)
