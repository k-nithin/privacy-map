"""Abstract base detector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Detection:
    """A single detection result."""
    detector_type: str  # pii, secrets, sensitivity
    label: str  # email, phone, api_key, hr, finance, etc.
    confidence: float  # 0.0 to 1.0
    matched_text: str = ""  # masked or truncated snippet


class BaseDetector(ABC):
    """Base interface for content detectors."""

    @property
    @abstractmethod
    def detector_type(self) -> str:
        """Return detector category name."""

    @abstractmethod
    def detect(self, text: str) -> list[Detection]:
        """Run detection on a text sample. Returns list of Detections."""
