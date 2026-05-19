# Configuration

AI PBOM uses two config files: a **scan config** (data sources + detectors) and an **app manifest** (AI applications + their data dependencies).

## Scan Config (`config/config.yaml`)

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
    exclude_patterns:
      - "*.tmp"

sampling:
  max_rows_per_table: 100       # rows sampled per Postgres table
  max_files_per_directory: 50   # files sampled per directory
  max_text_chars: 10000         # character limit per sample

detectors:
  pii: true
  secrets: true
  sensitivity: true
  custom:
    config_path: config/custom_detectors.yaml
```

### Supported Source Types

| Type | Description |
|------|-------------|
| `postgres` | Standard PostgreSQL tables |
| `pgvector` | Vector embedding tables (requires pgvector extension) |
| `filesystem` | Local files and directories |

### Sampling

Sampling limits keep scans fast and bounded. Increase them for deeper coverage at the cost of scan time. The report flags assets where less than 1% of rows were sampled so you know when a score may be conservative.

## App Manifest (`config/apps.yaml`)

```yaml
applications:
  - app_id: customer-chatbot
    app_type: chatbot
    model_provider: openai
    model_name: gpt-4
    external_endpoint: https://api.openai.com/v1/chat/completions
    declared_dependencies:
      - pg:public.prompt_logs
      - fs:./data/documents

  - app_id: internal-assistant
    app_type: copilot
    model_provider: local
    model_name: llama-3-8b
    declared_dependencies:
      - fs:./data/documents
```

### App Fields

| Field | Required | Description |
|-------|----------|-------------|
| `app_id` | Yes | Unique identifier |
| `app_type` | Yes | `chatbot`, `copilot`, `classifier`, `analytics`, etc. |
| `model_provider` | Yes | `openai`, `anthropic`, `local`, etc. |
| `model_name` | Yes | Model identifier |
| `external_endpoint` | No | URL if the app calls an external model API |
| `declared_dependencies` | No | Asset IDs this app depends on |

### Dependency ID Format

Dependencies reference asset IDs in the form `<connector>:<location>`:

- `pg:public.users` — Postgres table `users` in schema `public`
- `fs:./data/prompt_logs` — filesystem path
- `pgvec:public.embeddings` — pgvector table
