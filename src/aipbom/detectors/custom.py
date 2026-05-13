"""Company-specific sensitive data detector.

Two layers:
1. Built-in defaults — common employee/internal data patterns shipped with the tool
2. Custom wrapper — user-editable config/custom_detectors.yaml loaded on top of defaults

Users can add patterns, add keywords, or disable specific defaults.
"""

import logging
import re
from pathlib import Path

import yaml

from aipbom.detectors.base import BaseDetector, Detection

logger = logging.getLogger(__name__)

# --- Built-in default patterns (always active unless disabled) ---

DEFAULT_PATTERNS = [
    {"label": "employee_id", "regex": r"\b(?:EMP|emp)[-_\s]?\d{4,}\b", "confidence": 0.85},
    {"label": "badge_number", "regex": r"\b(?:badge|BADGE)[-_\s:#]?\d{4,}\b", "confidence": 0.8},
    {"label": "payroll_id", "regex": r"\b(?:payroll|PAYROLL)[-_\s:#]?\d{4,}\b", "confidence": 0.85},
    {"label": "employee_name_field", "regex": r"(?i)(?:employee[_\s]?name|emp[_\s]?name)[:\s=]+\S+", "confidence": 0.75},
]

DEFAULT_KEYWORDS = [
    {
        "label": "employee_data",
        "terms": [
            "employee id", "emp id", "badge number", "payroll number",
            "direct deposit", "w-2", "w2 form", "i-9", "employment verification",
            "hire date", "termination date", "last day", "severance",
        ],
        "confidence": 0.75,
    },
]


def load_custom_config(path: str | Path | None) -> dict:
    """Load user custom_detectors.yaml and return parsed config."""
    if path is None:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _compile_pattern(p: dict) -> dict | None:
    try:
        return {
            "label": p["label"],
            "regex": re.compile(p["regex"], re.IGNORECASE),
            "confidence": p.get("confidence", 0.8),
        }
    except (re.error, KeyError) as e:
        logger.warning("Skipping invalid custom pattern %s: %s", p.get("label", "?"), e)
        return None


class CustomDetector(BaseDetector):
    """Detector for company-specific sensitive data.

    Loads built-in defaults first, then merges user-defined patterns
    and keywords from custom_detectors.yaml.
    """

    def __init__(self, custom_config_path: str | Path | None = None):
        user_cfg = load_custom_config(custom_config_path)
        disabled = set(user_cfg.get("disable_defaults", []))

        # Start with defaults (filtered by disable list)
        all_patterns = [p for p in DEFAULT_PATTERNS if p["label"] not in disabled]
        all_keywords = [k for k in DEFAULT_KEYWORDS if k["label"] not in disabled]

        # Merge user-defined patterns and keywords on top
        all_patterns.extend(user_cfg.get("patterns", []))
        all_keywords.extend(user_cfg.get("keywords", []))

        # Compile regex patterns
        self._patterns = []
        for p in all_patterns:
            compiled = _compile_pattern(p)
            if compiled:
                self._patterns.append(compiled)

        self._keywords = []
        for kw in all_keywords:
            self._keywords.append({
                "label": kw["label"],
                "terms": [t.lower() for t in kw.get("terms", [])],
                "confidence": kw.get("confidence", 0.7),
            })

    @property
    def detector_type(self) -> str:
        return "custom"

    def detect(self, text: str) -> list[Detection]:
        detections = []

        # Pattern-based detection
        for p in self._patterns:
            matches = p["regex"].findall(text)
            for match in matches:
                detections.append(Detection(
                    detector_type=self.detector_type,
                    label=p["label"],
                    confidence=p["confidence"],
                    matched_text=_mask(match if isinstance(match, str) else match[0]),
                ))

        # Keyword-based detection
        text_lower = text.lower()
        for kw in self._keywords:
            matched_terms = [t for t in kw["terms"] if t in text_lower]
            if matched_terms:
                detections.append(Detection(
                    detector_type=self.detector_type,
                    label=kw["label"],
                    confidence=kw["confidence"],
                    matched_text=f"matched {len(matched_terms)} terms",
                ))

        return detections


def _mask(text: str) -> str:
    if len(text) <= 4:
        return "***"
    return text[:2] + "***" + text[-2:]
