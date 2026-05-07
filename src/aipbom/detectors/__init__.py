"""Privacy and sensitivity detectors."""

from aipbom.detectors.pii import PiiDetector
from aipbom.detectors.secrets import SecretsDetector
from aipbom.detectors.sensitivity import SensitivityDetector

DETECTOR_REGISTRY: dict[str, type] = {
    "pii": PiiDetector,
    "secrets": SecretsDetector,
    "sensitivity": SensitivityDetector,
}


def get_active_detectors(detector_config: dict) -> list:
    """Return instantiated detectors based on config flags."""
    active = []
    for name, cls in DETECTOR_REGISTRY.items():
        if detector_config.get(name, True):
            active.append(cls())
    return active
