"""Privacy and sensitivity detectors."""

from aipbom.detectors.pii import PiiDetector
from aipbom.detectors.secrets import SecretsDetector
from aipbom.detectors.sensitivity import SensitivityDetector
from aipbom.detectors.custom import CustomDetector

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

    # Custom detector — loads defaults + user wrapper config
    custom_cfg = detector_config.get("custom", {})
    if custom_cfg is not False:
        config_path = custom_cfg.get("config_path") if isinstance(custom_cfg, dict) else None
        active.append(CustomDetector(custom_config_path=config_path))

    return active
