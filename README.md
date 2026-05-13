# AI PBOM — AI Privacy Posture & Data Map

A local-first, read-only CLI tool that inventories AI-related data assets, detects privacy-relevant content, maps those assets to AI applications, and produces explainable risk scores with actionable reports.

## Problem

Organizations use AI systems without visibility into what sensitive data those systems access. Prompt logs accumulate PII, vector stores embed confidential content, and training datasets contain credentials — all without a clear inventory or risk assessment. AI PBOM makes this visible.

## What It Does

- **Discovers** AI-related data assets (tables, vector stores, prompt logs, training data, files)
- **Detects** PII, secrets/credentials, and sensitive domain content (HR, finance, health, legal)
- **Maps** data assets to AI applications based on declared dependencies
- **Scores** risk with an additive, explainable model
- **Reports** findings in machine-readable JSON and a human-readable Markdown report

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install

```bash
git clone https://github.com/nithinkakani/privacy-map.git
cd privacy-map
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run the Demo

A self-contained demo with sample data is included — no database or external services needed:

```bash
./demo.sh
```

This scans synthetic prompt logs, training data, and documents, then outputs a full privacy risk report to `demo/output/report.md`.

### Sample Output

<details>
<summary>Click to expand sample report output</summary>

```
# AI PBOM Report

## Scan Summary

- Assets discovered: 9
- Applications mapped: 3
- Relationships identified: 5
- Findings generated: 17

## Top Findings

### [CRITICAL] secrets — fs:demo/sample_data/documents/api_integration_notes.md

Secrets/credentials found in file: generic_api_key, slack_token, bearer_token, aws_access_key

- Evidence: sample_size=1, match_count=4, match_rate=400.0%

### [HIGH] pii — fs:demo/sample_data/prompt_logs

PII detected in prompt_logs: email, phone, customer_id, ssn, date_of_birth

- Evidence: sample_size=2, match_count=5, match_rate=250.0%

### [MEDIUM] sensitivity — fs:demo/sample_data/training

Sensitive domain content in training_data: customer_support, finance, hr

- Evidence: sample_size=1, match_count=3, match_rate=300.0%

## Top Risky Assets

### fs:demo/sample_data/documents — Score: 70 (critical)

- PII detected in content
- Secrets/credentials detected
- Sensitive domain content detected

### fs:demo/sample_data/training — Score: 50 (high)

- PII detected in content
- Sensitive domain content detected
- Asset is training data

### fs:demo/sample_data/prompt_logs — Score: 45 (medium)

- PII detected in content
- Asset is a prompt log store

## Top Risky Applications

### customer-support-bot — Score: 20 (low)

- Uses external endpoint: https://api.openai.com/v1/chat/completions

## Remediation Recommendations

1. Rotate exposed credentials and remove secrets from AI data stores immediately.
2. Review and minimize PII in prompt logs, training data, and vector stores.
3. Prioritize remediation of critical-risk assets.
4. Audit data sent to external model endpoints for sensitive content leakage.
5. Apply access controls to assets containing HR, finance, health, or legal data.
```

</details>

### Run Against Your Own Data

```bash
# Full pipeline (scan → build → report)
aipbom run --config config/config.yaml --apps config/apps.yaml --out output/

# Or run steps individually
aipbom scan   --config config/config.yaml --apps config/apps.yaml --out output/
aipbom build  --config config/config.yaml --apps config/apps.yaml --out output/
aipbom report --pbom output/pbom.json --out output/report.md
```

### Outputs

| File | Description |
|------|-------------|
| `assets.json` | Discovered asset inventory |
| `findings.json` | Privacy-relevant findings with evidence |
| `pbom.json` | Complete PBOM artifact (assets + apps + relationships + risk scores) |
| `report.md` | Human-readable report with remediation recommendations |

## Configuration

### Scan Config (`config/config.yaml`)

Defines data sources to scan, sampling limits, and which detectors to enable:

```yaml
data_sources:
  - type: postgres
    connection:
      host: localhost
      port: 5432
      database: myapp
      user: postgres
      password: postgres
    schemas:
      - public

  - type: filesystem
    paths:
      - ./data/prompt_logs
      - ./data/documents
    include_patterns:
      - "*.json"
      - "*.jsonl"
      - "*.txt"

sampling:
  max_rows_per_table: 100
  max_files_per_directory: 50
  max_text_chars: 10000

detectors:
  pii: true
  secrets: true
  sensitivity: true
```

### App Manifest (`config/apps.yaml`)

Declares AI applications and their data dependencies:

```yaml
applications:
  - app_id: customer-chatbot
    app_type: chatbot
    model_provider: openai
    model_name: gpt-4
    external_endpoint: https://api.openai.com/v1/chat/completions
    declared_dependencies:
      - pg:public.prompt_logs
      - pgvec:public.embeddings
```

## Connectors

| Connector | Purpose |
|-----------|---------|
| `postgres` | Structured tables in PostgreSQL |
| `pgvector` | Vector embedding tables (pgvector extension) |
| `filesystem` | Local files and directories |

## Detectors

| Detector | What It Finds |
|----------|---------------|
| PII | Email, phone, SSN, customer IDs, date of birth, addresses |
| Secrets | API keys, bearer tokens, private keys, AWS/GitHub/Slack tokens |
| Sensitivity | HR, finance, health, legal, and customer support content |
| Custom | Company-specific patterns and keywords (user-configurable) |

### Custom Detector

The custom detector ships with built-in defaults for common employee data (employee ID, badge number, payroll ID) and loads additional patterns from `config/custom_detectors.yaml`.

Edit the wrapper config to add your own:

```yaml
# config/custom_detectors.yaml

# Add company-specific regex patterns
patterns:
  - label: emp_nbr
    regex: "\\bW[-\\s]?\\d{6,}\\b"
    confidence: 0.9

# Add keyword groups
keywords:
  - label: internal_projects
    terms: ["project alpha", "codename phoenix"]
    confidence: 0.8

# Disable any built-in defaults you don't need
# disable_defaults:
#   - badge_number
```

Built-in defaults run automatically. User patterns merge on top. No code changes needed.

## Risk Scoring

Scores are additive and explainable. Each asset and application gets a score (0–100) mapped to a severity level:

| Score | Level |
|-------|-------|
| 0–24 | Low |
| 25–49 | Medium |
| 50–69 | High |
| 70–100 | Critical |

Every score includes a list of **drivers** explaining why it increased — no black-box scoring.

## Project Structure

```
privacy-map/
├── pyproject.toml              # Package definition and dependencies
├── demo.sh                     # One-command runnable demo
├── demo/
│   ├── config.yaml             # Demo scan config
│   ├── apps.yaml               # Demo app manifest
│   └── sample_data/            # Synthetic test data (no real PII)
├── src/aipbom/
│   ├── cli.py                  # Click CLI entry point
│   ├── config.py               # YAML config parsing
│   ├── pipeline.py             # Orchestrates scan/build/report
│   ├── connectors/             # Postgres, pgvector, filesystem
│   ├── detectors/              # PII, secrets, sensitivity
│   ├── models/                 # Asset, Application, Finding, RiskSummary
│   ├── scoring/                # Additive risk scoring engine
│   ├── mapping/                # App-to-asset dependency mapping
│   └── output/                 # JSON + Markdown writers
├── config/                     # Example configuration files
└── tests/                      # Unit tests (28 passing)
```

## Testing

```bash
pytest tests/ -v
```

## Design Principles

- **Read-only** — never modifies source systems
- **Pluggable** — connectors and detectors implement base interfaces for extensibility
- **Explainable** — every risk score has traceable drivers
- **Bounded** — sampling limits prevent runaway memory and time usage
- **Privacy-aware** — outputs use counts and masked evidence, not raw sensitive values

## License

MIT
