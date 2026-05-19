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

"""PII detector using regex patterns."""

import re

from aipbom.detectors.base import BaseDetector, Detection

# Patterns for common PII types
PATTERNS: list[tuple[str, re.Pattern, float]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), 0.9),
    ("phone", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), 0.8),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), 0.95),
    ("customer_id", re.compile(r"\b(?:customer|cust|account|acct)[_-]?(?:id|no|num)[:\s]*\w+", re.IGNORECASE), 0.7),
    ("date_of_birth", re.compile(r"\b(?:dob|date.of.birth|birth.?date)[:\s]*\d{1,4}[-/]\d{1,2}[-/]\d{1,4}", re.IGNORECASE), 0.8),
    ("address", re.compile(r"\b\d{1,5}\s+\w+\s+(?:st|street|ave|avenue|blvd|boulevard|rd|road|dr|drive|ln|lane|ct|court)\b", re.IGNORECASE), 0.6),
]


def _mask(text: str) -> str:
    """Mask detected text for evidence without exposing raw PII."""
    if len(text) <= 4:
        return "***"
    return text[:2] + "***" + text[-2:]


class PiiDetector(BaseDetector):
    """Regex-based PII detector."""

    @property
    def detector_type(self) -> str:
        return "pii"

    def detect(self, text: str) -> list[Detection]:
        detections = []
        for label, pattern, confidence in PATTERNS:
            matches = pattern.findall(text)
            for match in matches:
                detections.append(Detection(
                    detector_type=self.detector_type,
                    label=label,
                    confidence=confidence,
                    matched_text=_mask(match),
                ))
        return detections
