"""Pipeline orchestrator — ties scan, build, and report together."""

import json
import logging
import uuid
from pathlib import Path

from aipbom.config import load_scan_config, load_app_manifest, resolve_output_dir
from aipbom.connectors import get_connector
from aipbom.detectors import get_active_detectors
from aipbom.detectors.base import Detection
from aipbom.mapping.app_mapper import map_applications
from aipbom.models import Asset, Application, Finding, RiskSummary
from aipbom.output.json_writer import write_assets, write_findings, write_pbom
from aipbom.output.report import generate_report
from aipbom.scoring.engine import score_asset, score_application

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_scan(config_path: str, apps_path: str, out_path: str) -> None:
    """Discover assets, sample content, run detectors, write findings."""
    config = load_scan_config(config_path)
    output_dir = resolve_output_dir(out_path)

    # Discover
    logger.info("Starting asset discovery...")
    assets = _discover_all(config)
    logger.info("Discovered %d assets", len(assets))

    # Sample and detect
    logger.info("Running detectors...")
    findings = _detect_all(config, assets)
    logger.info("Generated %d findings", len(findings))

    # Classify assets based on findings
    _classify_assets(assets, findings)

    # Write intermediate outputs
    write_assets(assets, output_dir)
    write_findings(findings, output_dir)
    logger.info("Scan complete. Outputs written to %s", output_dir)


def run_build(config_path: str, apps_path: str, out_path: str) -> None:
    """Map assets to apps, score risks, write PBOM."""
    config = load_scan_config(config_path)
    applications = load_app_manifest(apps_path)
    output_dir = resolve_output_dir(out_path)

    # Load scan outputs
    assets = _load_assets(output_dir)
    findings = _load_findings(output_dir)

    # Map
    relationships = map_applications(applications, assets)
    logger.info("Mapped %d relationships", len(relationships))

    # Score
    asset_risks = [score_asset(a, findings) for a in assets]
    asset_risk_map = {r.subject_id: r for r in asset_risks}
    app_risks = [
        score_application(app, assets, findings, asset_risk_map)
        for app in applications
    ]

    # Write PBOM
    write_pbom(assets, applications, relationships, findings, asset_risks, app_risks, output_dir)
    logger.info("PBOM written to %s/pbom.json", output_dir)


def run_report(pbom_path: str, out_path: str) -> None:
    """Generate Markdown report from PBOM."""
    pbom = json.loads(Path(pbom_path).read_text())

    assets = [Asset(**a) for a in pbom["assets"]]
    applications = [_app_from_dict(a) for a in pbom["applications"]]

    from aipbom.mapping.app_mapper import Relationship
    relationships = [Relationship(**r) for r in pbom["relationships"]]
    findings = [Finding(**f) for f in pbom["findings"]]
    asset_risks = [RiskSummary(**r) for r in pbom["risk_summaries"]["assets"]]
    app_risks = [RiskSummary(**r) for r in pbom["risk_summaries"]["applications"]]

    out = Path(out_path)
    if out.is_dir():
        out = out / "report.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    generate_report(assets, applications, relationships, findings, asset_risks, app_risks, out)
    logger.info("Report written to %s", out)


def run_all(config_path: str, apps_path: str, out_path: str) -> None:
    """Execute scan, build, and report in sequence."""
    run_scan(config_path, apps_path, out_path)
    run_build(config_path, apps_path, out_path)

    output_dir = resolve_output_dir(out_path)
    pbom_path = str(output_dir / "pbom.json")
    run_report(pbom_path, str(output_dir / "report.md"))


# --- Internal helpers ---


def _discover_all(config: dict) -> list[Asset]:
    """Run discovery across all configured data sources."""
    assets = []
    for source in config["data_sources"]:
        try:
            connector = get_connector(source)
            discovered = connector.discover()
            assets.extend(discovered)
            connector.close()
        except Exception as e:
            logger.error("Failed to connect to source %s: %s", source.get("type"), e)
    return assets


def _detect_all(config: dict, assets: list[Asset]) -> list[Finding]:
    """Sample each asset and run detectors."""
    detectors = get_active_detectors(config.get("detectors", {}))
    sampling = config["sampling"]
    findings = []

    for asset in assets:
        samples = _sample_asset(config, asset, sampling)
        if not samples:
            continue

        asset.sample_size = len(samples)
        all_detections: list[Detection] = []

        for text in samples:
            for detector in detectors:
                all_detections.extend(detector.detect(text))

        # Aggregate detections into findings
        findings.extend(_detections_to_findings(asset, all_detections, len(samples)))

    return findings


def _sample_asset(config: dict, asset: Asset, sampling: dict) -> list[str]:
    """Sample content from an asset using its connector."""
    source = _find_source_for_asset(config, asset)
    if not source:
        return []

    try:
        connector = get_connector(source)
        samples = connector.sample(
            asset,
            max_rows=sampling["max_rows_per_table"],
            max_chars=sampling["max_text_chars"],
        )
        connector.close()
        return samples
    except Exception as e:
        logger.warning("Failed to sample %s: %s", asset.asset_id, e)
        return []


def _find_source_for_asset(config: dict, asset: Asset) -> dict | None:
    """Find the data source config that produced this asset."""
    for source in config["data_sources"]:
        if source["type"] == asset.store_type:
            return source
        if source["type"] == "pgvector" and asset.store_type == "pgvector":
            return source
    return None


def _detections_to_findings(
    asset: Asset, detections: list[Detection], sample_size: int
) -> list[Finding]:
    """Aggregate detections into per-category findings for an asset."""
    if not detections:
        return []

    # Group by (detector_type, label)
    groups: dict[str, list[Detection]] = {}
    for d in detections:
        groups.setdefault(d.detector_type, []).append(d)

    findings = []
    for category, dets in groups.items():
        labels = list({d.label for d in dets})
        match_count = len(dets)
        max_confidence = max(d.confidence for d in dets)
        severity = _severity_from_detection(category, match_count, max_confidence)

        finding = Finding(
            finding_id=f"F-{uuid.uuid4().hex[:8]}",
            subject_id=asset.asset_id,
            subject_type="asset",
            severity=severity,
            category=category,
            description=_describe_finding(category, labels, asset),
            evidence={
                "sample_size": sample_size,
                "match_count": match_count,
                "match_rate": f"{match_count / max(sample_size, 1):.1%}",
                "labels_detected": labels,
                "max_confidence": max_confidence,
            },
        )
        findings.append(finding)

    return findings


def _severity_from_detection(category: str, count: int, confidence: float) -> str:
    if category == "secrets" and confidence >= 0.9:
        return "critical"
    if category == "pii" and count >= 5:
        return "high"
    if category == "pii" and confidence >= 0.8:
        return "medium"
    if category == "sensitivity":
        return "medium" if count >= 3 else "low"
    if count >= 3:
        return "high"
    return "medium"


def _describe_finding(category: str, labels: list[str], asset: Asset) -> str:
    label_str = ", ".join(labels[:5])
    if category == "pii":
        return f"PII detected in {asset.asset_type} '{asset.location}': {label_str}"
    if category == "secrets":
        return f"Secrets/credentials found in {asset.asset_type} '{asset.location}': {label_str}"
    if category == "sensitivity":
        return f"Sensitive domain content in {asset.asset_type} '{asset.location}': {label_str}"
    return f"{category} detected in '{asset.location}'"


def _classify_assets(assets: list[Asset], findings: list[Finding]) -> None:
    """Update asset classification based on findings."""
    for asset in assets:
        asset_findings = [f for f in findings if f.subject_id == asset.asset_id]
        asset.classification = list({f.category for f in asset_findings})


def _load_assets(output_dir: Path) -> list[Asset]:
    path = output_dir / "assets.json"
    if not path.exists():
        raise FileNotFoundError(f"Run 'aipbom scan' first — {path} not found")
    data = json.loads(path.read_text())
    return [Asset(**a) for a in data]


def _load_findings(output_dir: Path) -> list[Finding]:
    path = output_dir / "findings.json"
    if not path.exists():
        raise FileNotFoundError(f"Run 'aipbom scan' first — {path} not found")
    data = json.loads(path.read_text())
    return [Finding(**f) for f in data]


def _app_from_dict(d: dict) -> Application:
    """Deserialize Application from dict, ignoring computed fields."""
    return Application(
        app_id=d["app_id"],
        app_type=d["app_type"],
        model_provider=d["model_provider"],
        model_name=d["model_name"],
        external_endpoint=d.get("external_endpoint"),
        declared_dependencies=d.get("declared_dependencies", []),
    )
