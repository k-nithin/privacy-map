"""Configuration parsing and validation."""

from pathlib import Path
from typing import Any

import yaml

from aipbom.models import Application


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_scan_config(path: str) -> dict[str, Any]:
    """Load and validate scan configuration."""
    raw = load_yaml(path)

    config = {
        "data_sources": raw.get("data_sources", []),
        "sampling": {
            "max_rows_per_table": raw.get("sampling", {}).get("max_rows_per_table", 100),
            "max_files_per_directory": raw.get("sampling", {}).get("max_files_per_directory", 50),
            "max_text_chars": raw.get("sampling", {}).get("max_text_chars", 10000),
        },
        "detectors": raw.get("detectors", {"pii": True, "secrets": True, "sensitivity": True}),
        "output_dir": raw.get("output_dir", "output/"),
    }

    if not config["data_sources"]:
        raise ValueError("config.yaml must define at least one data source")

    return config


def load_app_manifest(path: str) -> list[Application]:
    """Load application manifest into Application objects."""
    raw = load_yaml(path)
    apps = []
    for entry in raw.get("applications", []):
        apps.append(Application(
            app_id=entry["app_id"],
            app_type=entry.get("app_type", "unknown"),
            model_provider=entry.get("model_provider", "unknown"),
            model_name=entry.get("model_name", "unknown"),
            external_endpoint=entry.get("external_endpoint"),
            declared_dependencies=entry.get("declared_dependencies", []),
        ))
    return apps


def resolve_output_dir(cli_out: str) -> Path:
    """Ensure output directory exists and return Path."""
    out = Path(cli_out)
    out.mkdir(parents=True, exist_ok=True)
    return out
