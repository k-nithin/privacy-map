# Copyright 2026 Nithin Kakani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Secrets and credential detector using regex patterns."""

import re

from aipbom.detectors.base import BaseDetector, Detection

PATTERNS: list[tuple[str, re.Pattern, float]] = [
    ("openai_api_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), 0.95),
    ("anthropic_api_key", re.compile(r"\bsk-ant-[A-Za-z0-9\-]{20,}\b"), 0.95),
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
