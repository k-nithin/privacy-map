# AI PBOM — AI Privacy Posture & Data Map

A local-first, read-only CLI that inventories AI data assets, detects PII and secrets, maps assets to applications, and produces explainable risk reports.

## What It Does

- **Discovers** tables, vector stores, prompt logs, training data, and files
- **Detects** PII, credentials, and sensitive domain content (HR, finance, health, legal)
- **Maps** data assets to AI applications via declared dependencies
- **Scores** risk with an additive, explainable model (0–100 per asset and app)
- **Reports** findings as JSON + a concise Markdown report

## Quick Start

```bash
git clone https://github.com/nithinkakani/privacy-map.git
cd privacy-map
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Run the self-contained demo (no database needed):

```bash
./demo.sh
cat demo/output/report.md
```

Run against your own data:

```bash
aipbom run --config config/config.yaml --apps config/apps.yaml --out output/
```

Or step by step:

```bash
aipbom scan   --config config/config.yaml --apps config/apps.yaml --out output/
aipbom build  --config config/config.yaml --apps config/apps.yaml --out output/
aipbom report --pbom output/pbom.json --out output/report.md
```

## Outputs

| File | Description |
|------|-------------|
| `assets.json` | Discovered asset inventory |
| `findings.json` | Findings with evidence |
| `pbom.json` | Full PBOM artifact (assets + apps + relationships + risk scores) |
| `report.md` | Human-readable report with recommendations |

## Docs

- [Configuration](docs/configuration.md) — scan config and app manifest reference
- [Detectors](docs/detectors.md) — PII, secrets, sensitivity, and custom patterns
- [Scoring](docs/scoring.md) — how risk scores are computed
- [Architecture](docs/architecture.md) — project structure and design principles

## Testing

```bash
pytest tests/
```

## License

MIT
