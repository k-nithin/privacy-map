"""Secrets and credential detector using regex patterns."""

import re

from aipbom.detectors.base import BaseDetector, Detection

PATTERNS: list[tuple[str, re.Pattern, float]] = [
    ("aws_access_key", re.compile(r"\b(?:AKIA)[A-Z0-9]{16}\b"), 0.95),
    ("aws_secret_key", re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"][A-Za-z0-9/+=]{40}['\"]"), 0.9),
    ("generic_api_key", re.compile(r"(?i)(?:api[_-]?key|apikey)[:\s=]+['\"]?[A-Za-z0-9_\-]{20,}['\"]?"), 0.85),
    ("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9_\-.]{20,}"), 0.9),
    ("generic_secret", re.compile(r"(?i)(?:secret|password|passwd|pwd)[:\s=]+['\"]?[^\s'\"]{8,}['\"]?"), 0.7),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"), 0.99),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}\b"), 0.95),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]+\b"), 0.9),
]


def _mask_secret(text: str) -> str:
    if len(text) <= 8:
        return "***"
    return text[:4] + "***" + text[-3:]


class SecretsDetector(BaseDetector):
    """Regex-based secrets and credential detector."""

    @property
    def detector_type(self) -> str:
        return "secrets"

    def detect(self, text: str) -> list[Detection]:
        detections = []
        for label, pattern, confidence in PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                detections.append(Detection(
                    detector_type=self.detector_type,
                    label=label,
                    confidence=confidence,
                    matched_text=_mask_secret(match),
                ))
        return detections
