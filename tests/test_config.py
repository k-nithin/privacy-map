"""Tests for configuration parsing."""

import tempfile
from pathlib import Path

import yaml

from aipbom.config import load_scan_config, load_app_manifest


def test_load_scan_config():
    config_data = {
        "data_sources": [{"type": "filesystem", "paths": ["/tmp/test"]}],
        "sampling": {"max_rows_per_table": 50},
        "detectors": {"pii": True, "secrets": False},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()
        config = load_scan_config(f.name)

    assert len(config["data_sources"]) == 1
    assert config["sampling"]["max_rows_per_table"] == 50
    assert config["detectors"]["secrets"] is False


def test_load_app_manifest():
    apps_data = {
        "applications": [
            {
                "app_id": "test-bot",
                "app_type": "chatbot",
                "model_provider": "openai",
                "model_name": "gpt-4",
                "external_endpoint": "https://api.openai.com/v1/chat",
                "declared_dependencies": ["pg:public.logs"],
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(apps_data, f)
        f.flush()
        apps = load_app_manifest(f.name)

    assert len(apps) == 1
    assert apps[0].app_id == "test-bot"
    assert apps[0].endpoint_type == "external"
    assert "pg:public.logs" in apps[0].declared_dependencies
