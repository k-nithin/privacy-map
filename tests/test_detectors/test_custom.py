"""Tests for company-specific custom detector."""

import tempfile
from pathlib import Path

import yaml

from aipbom.detectors.custom import CustomDetector, DEFAULT_PATTERNS


# --- Default patterns (built-in) ---

def test_defaults_detect_employee_id():
    detector = CustomDetector()
    results = detector.detect("Assigned to EMP-12345 for review.")
    assert any(d.label == "employee_id" for d in results)


def test_defaults_detect_badge_number():
    detector = CustomDetector()
    results = detector.detect("Badge number: badge-9876 issued.")
    assert any(d.label == "badge_number" for d in results)


def test_defaults_detect_payroll():
    detector = CustomDetector()
    results = detector.detect("Payroll 54321 updated for this cycle.")
    assert any(d.label == "payroll_id" for d in results)


def test_defaults_detect_employee_keywords():
    detector = CustomDetector()
    results = detector.detect("Submit W-2 form and employment verification by hire date.")
    assert any(d.label == "employee_data" for d in results)


def test_defaults_no_match():
    detector = CustomDetector()
    results = detector.detect("The sun is shining today.")
    assert results == []


# --- User wrapper config ---

def test_user_patterns_merged():
    cfg = {
        "patterns": [
            {"label": "emp_nbr", "regex": r"W-\d{6,}", "confidence": 0.9},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(cfg, f)
        f.flush()
        detector = CustomDetector(custom_config_path=f.name)

    results = detector.detect("EMP-9999 and W-1234567 on record.")
    labels = {d.label for d in results}
    assert "employee_id" in labels  # default
    assert "emp_nbr" in labels      # user-added


def test_disable_defaults():
    cfg = {
        "disable_defaults": ["badge_number", "payroll_id"],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(cfg, f)
        f.flush()
        detector = CustomDetector(custom_config_path=f.name)

    results = detector.detect("badge-1234 payroll 5678 EMP-9999")
    labels = {d.label for d in results}
    assert "employee_id" in labels
    assert "badge_number" not in labels
    assert "payroll_id" not in labels


def test_no_config_file_uses_defaults_only():
    detector = CustomDetector(custom_config_path="/nonexistent/path.yaml")
    results = detector.detect("EMP-12345 on file.")
    assert any(d.label == "employee_id" for d in results)


def test_masking():
    detector = CustomDetector()
    results = detector.detect("EMP-1234567890")
    for d in results:
        if d.label == "employee_id":
            assert "***" in d.matched_text
