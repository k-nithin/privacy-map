"""Tests for risk scoring engine."""

from aipbom.models import Asset, Application, Finding, RiskSummary
from aipbom.scoring.engine import score_asset, score_application


def _make_asset(asset_id="test-asset", asset_type="table"):
    return Asset(
        asset_id=asset_id,
        asset_type=asset_type,
        store_type="postgres",
        location="public.test",
    )


def _make_finding(subject_id="test-asset", category="pii", severity="medium"):
    return Finding(
        finding_id="F-001",
        subject_id=subject_id,
        subject_type="asset",
        severity=severity,
        category=category,
        description="Test finding",
    )


def test_score_asset_no_findings():
    asset = _make_asset()
    result = score_asset(asset, [])
    assert result.risk_score == 0
    assert result.risk_level == "low"


def test_score_asset_with_pii():
    asset = _make_asset()
    findings = [_make_finding(category="pii")]
    result = score_asset(asset, findings)
    assert result.risk_score >= 25
    assert "PII detected" in result.drivers[0]


def test_score_asset_prompt_logs():
    asset = _make_asset(asset_type="prompt_logs")
    findings = [_make_finding(category="pii")]
    result = score_asset(asset, findings)
    assert result.risk_score >= 45
    assert any("prompt log" in d for d in result.drivers)


def test_score_asset_critical():
    asset = _make_asset(asset_type="prompt_logs")
    findings = [
        _make_finding(category="pii"),
        _make_finding(category="secrets"),
        _make_finding(category="sensitivity"),
    ]
    result = score_asset(asset, findings)
    assert result.risk_level in ("high", "critical")


def test_score_application_external():
    app = Application(
        app_id="test-app",
        app_type="chatbot",
        model_provider="openai",
        model_name="gpt-4",
        external_endpoint="https://api.openai.com/v1/chat",
        declared_dependencies=["test-asset"],
    )
    asset = _make_asset()
    findings = [_make_finding(category="pii")]
    asset_risks = {"test-asset": RiskSummary(
        subject_id="test-asset", subject_type="asset",
        risk_score=50, risk_level="high", drivers=["PII"]
    )}

    result = score_application(app, [asset], findings, asset_risks)
    assert result.risk_score >= 20
    assert any("external" in d.lower() for d in result.drivers)
