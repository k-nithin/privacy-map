"""Finding data model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    finding_id: str
    subject_id: str
    subject_type: str  # asset or application
    severity: str  # low, medium, high, critical
    category: str  # pii, secrets, sensitivity, external_endpoint, vector_store
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "evidence": self.evidence,
        }
