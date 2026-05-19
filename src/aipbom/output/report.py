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

"""Markdown report generator."""

from datetime import date
from pathlib import Path

from aipbom.mapping.app_mapper import Relationship
from aipbom.models import Application, Asset, Finding, RiskSummary

_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def generate_report(
    assets: list[Asset],
    applications: list[Application],
    relationships: list[Relationship],
    findings: list[Finding],
    asset_risks: list[RiskSummary],
    app_risks: list[RiskSummary],
    output_path: Path,
) -> Path:
    """Generate a human-readable Markdown report."""
    # Show only directory/table-level assets — individual files are noise at report level
    summary_assets = [a for a in assets if not a.schema_info.get("extension")]
    summary_ids = {a.asset_id for a in summary_assets}
    risk_by_asset = {r.subject_id: r for r in asset_risks}
    risk_by_app = {r.subject_id: r for r in app_risks}

    lines: list[str] = []

    lines += [
        "# AI Privacy Risk Report",
        "",
        f"Scan date: {date.today()}  |  "
        f"Assets: {len(summary_assets)}  |  "
        f"Applications: {len(applications)}  |  "
        f"Findings: {len(findings)}",
        "",
    ]

    _write_overview(lines, summary_assets, risk_by_asset, app_risks)
    _write_key_findings(lines, findings, summary_ids)
    _write_asset_table(lines, summary_assets, risk_by_asset)
    _write_app_table(lines, applications, risk_by_app)
    _write_recommendations(lines, findings, asset_risks, app_risks)

    output_path.write_text("\n".join(lines))
    return output_path


# --- Sections ---

def _write_overview(
    lines: list[str],
    summary_assets: list[Asset],
    risk_by_asset: dict[str, RiskSummary],
    app_risks: list[RiskSummary],
) -> None:
    asset_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for a in summary_assets:
        r = risk_by_asset.get(a.asset_id)
        if r:
            asset_counts[r.risk_level] = asset_counts.get(r.risk_level, 0) + 1

    app_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for r in app_risks:
        app_counts[r.risk_level] = app_counts.get(r.risk_level, 0) + 1

    lines += [
        "## Risk Overview",
        "",
        "| Level    | Assets | Applications |",
        "|----------|--------|--------------|",
        f"| Critical | {asset_counts['critical']}      | {app_counts['critical']}            |",
        f"| High     | {asset_counts['high']}      | {app_counts['high']}            |",
        f"| Medium   | {asset_counts['medium']}      | {app_counts['medium']}            |",
        f"| Low      | {asset_counts['low']}      | {app_counts['low']}            |",
        "",
    ]


def _write_key_findings(
    lines: list[str],
    findings: list[Finding],
    summary_ids: set[str],
) -> None:
    """Critical and high findings only, from top-level assets."""
    key = sorted(
        [f for f in findings if f.subject_id in summary_ids and _severity_rank(f.severity) >= 3],
        key=lambda f: _severity_rank(f.severity),
        reverse=True,
    )

    lines += ["## Key Findings", ""]

    if not key:
        lines += ["No critical or high severity findings detected.", ""]
        return

    lines += [
        "| Severity | Category | Asset | Detected |",
        "|----------|----------|-------|---------|",
    ]
    for f in key:
        labels = ", ".join(f.evidence.get("labels_detected", [])[:5])
        lines.append(
            f"| **{f.severity.upper()}** | {f.category} | {_short_path(f.subject_id)} | {labels} |"
        )
    lines.append("")


def _write_asset_table(
    lines: list[str],
    summary_assets: list[Asset],
    risk_by_asset: dict[str, RiskSummary],
) -> None:
    sorted_assets = sorted(
        summary_assets,
        key=lambda a: _severity_rank(risk_by_asset[a.asset_id].risk_level)
        if a.asset_id in risk_by_asset else 0,
        reverse=True,
    )

    lines += [
        "## Asset Risk Summary",
        "",
        "| Asset | Type | Score | Level | Issues |",
        "|-------|------|-------|-------|--------|",
    ]
    for a in sorted_assets:
        r = risk_by_asset.get(a.asset_id)
        score = str(r.risk_score) if r else "—"
        level = r.risk_level.upper() if r else "—"
        issues = ", ".join(a.classification) if a.classification else "none"
        lines.append(
            f"| {_short_path(a.location)} | {a.asset_type} | {score} | {level} | {issues} |"
        )
    lines.append("")


def _write_app_table(
    lines: list[str],
    applications: list[Application],
    risk_by_app: dict[str, RiskSummary],
) -> None:
    sorted_apps = sorted(
        applications,
        key=lambda a: _severity_rank(risk_by_app[a.app_id].risk_level)
        if a.app_id in risk_by_app else 0,
        reverse=True,
    )

    lines += [
        "## Application Risk Summary",
        "",
        "| Application | Model | Endpoint | Score | Level |",
        "|-------------|-------|---------|-------|-------|",
    ]
    for app in sorted_apps:
        r = risk_by_app.get(app.app_id)
        score = str(r.risk_score) if r else "—"
        level = r.risk_level.upper() if r else "—"
        endpoint = "external" if app.external_endpoint else "local"
        model = f"{app.model_provider}/{app.model_name}"
        lines.append(f"| {app.app_id} | {model} | {endpoint} | {score} | {level} |")
    lines.append("")


def _write_recommendations(
    lines: list[str],
    findings: list[Finding],
    asset_risks: list[RiskSummary],
    app_risks: list[RiskSummary],
) -> None:
    lines += ["## Recommendations", ""]
    recs = _generate_recommendations(findings, asset_risks, app_risks)
    for i, rec in enumerate(recs, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")


# --- Helpers ---

def _short_path(path_str: str) -> str:
    """Return the last two path components for readability."""
    # Strip connector prefix (e.g. "fs:")
    clean = path_str.split(":", 1)[-1] if ":" in path_str else path_str
    parts = Path(clean).parts
    return "/".join(parts[-2:]) if len(parts) >= 2 else clean


def _severity_rank(severity: str) -> int:
    return _SEVERITY_RANK.get(severity, 0)


def _generate_recommendations(
    findings: list[Finding],
    asset_risks: list[RiskSummary],
    app_risks: list[RiskSummary],
) -> list[str]:
    recs = []
    categories = {f.category for f in findings}

    if "secrets" in categories:
        recs.append("Rotate exposed credentials and remove secrets from AI data stores immediately.")

    if "pii" in categories:
        recs.append("Review and minimize PII stored in prompt logs, training data, and vector stores.")

    critical_assets = [r for r in asset_risks if r.risk_level == "critical"]
    if critical_assets:
        names = ", ".join(_short_path(r.subject_id) for r in critical_assets[:3])
        recs.append(f"Prioritize remediation of critical-risk assets: {names}.")

    if any(any("external" in d.lower() for d in r.drivers) for r in app_risks):
        recs.append("Audit data flowing to external model endpoints for sensitive content leakage.")

    if "sensitivity" in categories:
        recs.append("Apply access controls to assets containing HR, finance, health, or legal content.")

    if not recs:
        recs.append("No critical findings detected. Continue periodic scanning to maintain visibility.")

    return recs
