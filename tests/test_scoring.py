"""Tests for risk scoring engine."""

from aipbom.models import Asset, Application, Finding, RiskSummary
from aipbom.scoring.engine import score_asset, score_application


def _make_asset(asset_id="test-asset", asset_type="table", schema_info=None, sample_size=0):
    return Asset(
        asset_id=asset_id,
        asset_type=asset_type,
        store_type="postgres",
        location="public.test",
        schema_info=schema_info or {},
        sample_size=sample_size,
    )


def _make_finding(subject_id="test-asset", category="pii", severity="medium", evidence=None):
    return Finding(
        finding_id="F-001",
        subject_id=subject_id,
        subject_type="asset",
        severity=severity,
        category=category,
        description="Test finding",
        evidence=evidence or {},
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


def test_score_asset_high_density_boosts_score():
    # 30% match rate + 95% confidence → density 1.4x * confidence 1.2x = 1.68x base
    asset = _make_asset()
    evidence = {"match_rate": "30.0%", "max_confidence": 0.95, "match_count": 15, "sample_size": 50}
    findings = [_make_finding(category="pii", evidence=evidence)]
    result = score_asset(asset, findings)
    # base 25 * 1.4 * 1.2 = 42
    assert result.risk_score >= 42


def test_score_asset_low_density_reduces_score():
    # 0.5% match rate + 65% confidence → density 0.6x * confidence 0.8x = 0.48x base
    asset = _make_asset()
    evidence = {"match_rate": "0.5%", "max_confidence": 0.65, "match_count": 1, "sample_size": 200}
    findings = [_make_finding(category="pii", evidence=evidence)]
    result = score_asset(asset, findings)
    # base 25 * 0.6 * 0.8 = 12
    assert result.risk_score <= 15


def test_score_asset_size_bonus_large():
    asset = _make_asset(schema_info={"row_count": 50_000})
    result = score_asset(asset, [])
    assert result.risk_score == 10
    assert any("Large data asset" in d for d in result.drivers)


def test_score_asset_size_bonus_medium():
    asset = _make_asset(schema_info={"size_bytes": 500_000})
    result = score_asset(asset, [])
    assert result.risk_score == 5
    assert any("Medium data asset" in d for d in result.drivers)


def test_score_asset_sampling_coverage_warning():
    # 10 rows sampled from a 50k-row table → 0.02% coverage
    asset = _make_asset(schema_info={"row_count": 50_000}, sample_size=10)
    findings = [_make_finding(category="pii")]
    result = score_asset(asset, findings)
    assert any("Warning" in d and "sampled" in d for d in result.drivers)


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
