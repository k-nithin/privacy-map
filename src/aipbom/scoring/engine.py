# Copyright 2026 Nithin Kakani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

_DETECTION_CATEGORIES = [
    ("pii", "pii_detected", "PII"),
    ("secrets", "secrets_detected", "Secrets/credentials"),
    ("sensitivity", "sensitivity_detected", "Sensitive domain content"),
]


def _level_from_score(score: int) -> str:
    if score >= 70:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def _parse_match_rate(rate_str: str) -> float:
    """Parse '24.0%' → 0.24."""
    try:
        return float(str(rate_str).strip("%")) / 100
    except (ValueError, AttributeError):
        return 0.0


def _density_factor(match_rate: float) -> float:
    """Scale weight by how pervasive detections are within sampled content."""
    if match_rate >= 0.10:
        return 1.4
    if match_rate >= 0.02:
        return 1.0
    return 0.6


def _confidence_factor(confidence: float) -> float:
    """Scale weight by detector confidence."""
    if confidence >= 0.9:
        return 1.2
    if confidence >= 0.7:
        return 1.0
    return 0.8


def _size_bonus(schema_info: dict) -> tuple[int, str]:
    """Additive bonus for large data assets (more exposure surface)."""
    size_bytes = schema_info.get("size_bytes") or 0
    row_count = schema_info.get("row_count") or 0
    if size_bytes >= 10_000_000 or row_count >= 10_000:
        return 10, "Large data asset (>10 MB / >10k rows)"
    if size_bytes >= 100_000 or row_count >= 100:
        return 5, "Medium data asset (>100 KB / >100 rows)"
    return 0, ""


def _sampling_coverage_drivers(asset: Asset) -> list[str]:
    """Warn when only a small fraction of a large asset was sampled."""
    sample_size = asset.sample_size
    if not sample_size:
        return []
    row_count = asset.schema_info.get("row_count") or 0
    size_bytes = asset.schema_info.get("size_bytes") or 0
    if row_count > 1000:
        coverage = sample_size / row_count
        if coverage < 0.01:
            return [f"Warning: {coverage:.1%} of rows sampled — score may underestimate actual risk"]
    elif size_bytes > 1_000_000 and sample_size < 10:
        return ["Warning: large file partially sampled — score may underestimate actual risk"]
    return []


def score_asset(asset: Asset, findings: list[Finding]) -> RiskSummary:
    """Compute risk score for a single asset based on its findings."""
    score = 0
    drivers = []

    asset_findings = [f for f in findings if f.subject_id == asset.asset_id]
    finding_by_category = {f.category: f for f in asset_findings}

    # Detection scoring — base weight scaled by match density and confidence
    for category, weight_key, label in _DETECTION_CATEGORIES:
        finding = finding_by_category.get(category)
        if not finding:
            continue
        evidence = finding.evidence
        if evidence:
            match_rate = _parse_match_rate(evidence.get("match_rate", "0%"))
            confidence = evidence.get("max_confidence", 0.8)
            match_count = evidence.get("match_count", 1)
            df = _density_factor(match_rate)
            cf = _confidence_factor(confidence)
            cat_score = round(ASSET_WEIGHTS[weight_key] * df * cf)
            drivers.append(
                f"{label} detected: {match_count} matches, "
                f"{evidence.get('match_rate')} density, "
                f"{confidence:.0%} confidence → +{cat_score}"
            )
        else:
            # No evidence — neutral factors
            cat_score = ASSET_WEIGHTS[weight_key]
            drivers.append(f"{label} detected → +{cat_score}")
        score += cat_score

    # Asset type structural bonuses (not scaled — inherent risk)
    for asset_type, weight_key, desc in [
        ("prompt_logs", "prompt_logs", "Asset is a prompt log store"),
        ("vector_table", "vector_table", "Asset is a vector store"),
        ("training_data", "training_data", "Asset is training data"),
        ("transcripts", "transcripts", "Asset contains transcripts"),
    ]:
        if asset.asset_type == asset_type:
            score += ASSET_WEIGHTS[weight_key]
            drivers.append(desc)

    # Data size bonus
    size_pts, size_desc = _size_bonus(asset.schema_info)
    if size_pts:
        score += size_pts
        drivers.append(size_desc)

    # Sampling coverage warnings (informational only — no score change)
    drivers.extend(_sampling_coverage_drivers(asset))

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
