"""Additive, explainable risk scoring engine."""

from aipbom.models import Asset, Application, Finding, RiskSummary

# Scoring weights — additive model
ASSET_WEIGHTS = {
    "pii_detected": 25,
    "secrets_detected": 30,
    "sensitivity_detected": 15,
    "prompt_logs": 20,
    "vector_table": 15,
    "training_data": 10,
    "transcripts": 10,
}

APP_WEIGHTS = {
    "external_endpoint": 20,
    "sensitive_dependency": 15,
    "multiple_sensitive_deps": 10,
    "pii_in_dependency": 20,
    "secrets_in_dependency": 25,
}


def _level_from_score(score: int) -> str:
    if score >= 70:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def score_asset(asset: Asset, findings: list[Finding]) -> RiskSummary:
    """Compute risk score for a single asset based on its findings."""
    score = 0
    drivers = []

    asset_findings = [f for f in findings if f.subject_id == asset.asset_id]

    categories_found = {f.category for f in asset_findings}

    if "pii" in categories_found:
        score += ASSET_WEIGHTS["pii_detected"]
        drivers.append("PII detected in content")

    if "secrets" in categories_found:
        score += ASSET_WEIGHTS["secrets_detected"]
        drivers.append("Secrets/credentials detected")

    if "sensitivity" in categories_found:
        score += ASSET_WEIGHTS["sensitivity_detected"]
        drivers.append("Sensitive domain content detected")

    if asset.asset_type == "prompt_logs":
        score += ASSET_WEIGHTS["prompt_logs"]
        drivers.append("Asset is a prompt log store")

    if asset.asset_type == "vector_table":
        score += ASSET_WEIGHTS["vector_table"]
        drivers.append("Asset is a vector store")

    if asset.asset_type == "training_data":
        score += ASSET_WEIGHTS["training_data"]
        drivers.append("Asset is training data")

    if asset.asset_type == "transcripts":
        score += ASSET_WEIGHTS["transcripts"]
        drivers.append("Asset contains transcripts")

    score = min(score, 100)

    return RiskSummary(
        subject_id=asset.asset_id,
        subject_type="asset",
        risk_score=score,
        risk_level=_level_from_score(score),
        drivers=drivers,
    )


def score_application(
    app: Application,
    assets: list[Asset],
    findings: list[Finding],
    asset_risks: dict[str, RiskSummary],
) -> RiskSummary:
    """Compute risk score for an application based on its dependencies."""
    score = 0
    drivers = []

    if app.external_endpoint:
        score += APP_WEIGHTS["external_endpoint"]
        drivers.append(f"Uses external endpoint: {app.external_endpoint}")

    dep_assets = [a for a in assets if a.asset_id in app.declared_dependencies]
    sensitive_deps = []

    for dep in dep_assets:
        dep_risk = asset_risks.get(dep.asset_id)
        if dep_risk and dep_risk.risk_level in ("high", "critical"):
            sensitive_deps.append(dep.asset_id)

    dep_findings = [f for f in findings if f.subject_id in app.declared_dependencies]
    dep_categories = {f.category for f in dep_findings}

    if "pii" in dep_categories:
        score += APP_WEIGHTS["pii_in_dependency"]
        drivers.append("PII found in application dependency")

    if "secrets" in dep_categories:
        score += APP_WEIGHTS["secrets_in_dependency"]
        drivers.append("Secrets found in application dependency")

    if sensitive_deps:
        score += APP_WEIGHTS["sensitive_dependency"]
        drivers.append(f"Depends on high-risk asset(s): {', '.join(sensitive_deps)}")

    if len(sensitive_deps) > 1:
        score += APP_WEIGHTS["multiple_sensitive_deps"]
        drivers.append("Multiple sensitive dependencies")

    score = min(score, 100)

    return RiskSummary(
        subject_id=app.app_id,
        subject_type="application",
        risk_score=score,
        risk_level=_level_from_score(score),
        drivers=drivers,
    )
