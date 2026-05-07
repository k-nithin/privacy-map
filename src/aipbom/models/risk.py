"""Risk summary data model."""

from dataclasses import dataclass, field


@dataclass
class RiskSummary:
    subject_id: str
    subject_type: str  # asset or application
    risk_score: int
    risk_level: str  # low, medium, high, critical
    drivers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "drivers": self.drivers,
        }
