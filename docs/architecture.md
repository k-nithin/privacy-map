# Architecture

## Pipeline

```
Config (YAML) → Connectors (discover + sample) → Detectors (classify)
    → Models (Asset, Finding) → Mapping (app→asset) → Scoring (risk)
        → Output (JSON + Markdown)
```

## Project Structure

```
privacy-map/
├── pyproject.toml
├── demo.sh                        # One-command demo
├── demo/
│   ├── config.yaml
│   ├── apps.yaml
│   └── sample_data/               # Synthetic data (no real PII)
├── config/                        # Example config files
├── src/aipbom/
│   ├── cli.py                     # Click CLI entry point
│   ├── config.py                  # YAML config parsing
│   ├── pipeline.py                # Orchestrates scan → build → report
│   ├── connectors/                # Postgres, pgvector, filesystem
│   ├── detectors/                 # PII, secrets, sensitivity, custom
│   ├── models/                    # Asset, Application, Finding, RiskSummary
│   ├── scoring/                   # Additive risk scoring engine
│   ├── mapping/                   # App-to-asset dependency mapping
│   └── output/                    # JSON + Markdown writers
└── tests/
```

## Key Interfaces

**Connector** — discovers assets and samples their content:
```python
connector.discover() -> list[Asset]
connector.sample(asset) -> list[str]
```

**Detector** — classifies text samples:
```python
detector.detect(text) -> list[Detection]
# Detection: type, label, confidence (0–1), matched_text (masked)
```

**Scorer** — computes risk from asset + findings:
```python
score_asset(asset, findings) -> RiskSummary
score_application(app, assets, findings, asset_risks) -> RiskSummary
```

## Design Principles

- **Read-only** — never modifies source systems
- **Pluggable** — connectors and detectors implement base interfaces; add new ones by registering in the `REGISTRY` dict
- **Explainable** — every risk score has traceable drivers; no black-box results
- **Bounded** — sampling limits in config prevent runaway memory and scan time
- **Privacy-aware** — outputs use counts and masked evidence, never raw sensitive values

## Adding a Connector

1. Subclass `BaseConnector` in `src/aipbom/connectors/`
2. Implement `discover()` and `sample()`
3. Register it in `src/aipbom/connectors/__init__.py`

## Adding a Detector

1. Subclass `BaseDetector` in `src/aipbom/detectors/`
2. Implement `detect(text) -> list[Detection]`
3. Register it in `src/aipbom/detectors/__init__.py`
