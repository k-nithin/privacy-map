# Detectors

Detectors scan sampled text and return typed detections with a confidence score (0.0–1.0). Each detection rolls up into a finding, which feeds the risk score.

## Built-in Detectors

### PII

Regex patterns for personal identifiable information:

| Label | Examples |
|-------|---------|
| `email` | user@example.com |
| `phone` | +1-555-000-1234, (555) 000-1234 |
| `ssn` | 123-45-6789 |
| `date_of_birth` | DOB: 01/15/1990 |
| `customer_id` | CUST-123456 |
| `credit_card` | 4111 1111 1111 1111 |
| `ip_address` | 192.168.1.1 |

### Secrets

Regex patterns for credentials and API keys:

| Label | Examples |
|-------|---------|
| `openai_api_key` | `sk-...` |
| `anthropic_api_key` | `sk-ant-...` |
| `aws_access_key` | `AKIA...` |
| `aws_secret_key` | `aws_secret_access_key = ...` |
| `github_token` | `ghp_...`, `ghs_...` |
| `slack_token` | `xoxb-...`, `xoxp-...` |
| `bearer_token` | `Authorization: Bearer ...` |
| `generic_api_key` | `api_key = ...` |
| `generic_secret` | `password = ...`, `secret = ...` |
| `private_key` | `-----BEGIN RSA PRIVATE KEY-----` |

### Sensitivity

Keyword-based domain classifier:

| Label | Trigger terms |
|-------|--------------|
| `hr` | employee, salary, performance review, termination, hiring |
| `finance` | revenue, P&L, budget, invoice, financial forecast |
| `health` | diagnosis, prescription, medical record, patient |
| `legal` | contract, litigation, attorney, NDA, compliance |
| `customer_support` | ticket, escalation, refund, churn |

## Custom Detector

Add company-specific patterns without writing code. Enable it in `config.yaml`:

```yaml
detectors:
  custom:
    config_path: config/custom_detectors.yaml
```

Then define patterns in `config/custom_detectors.yaml`:

```yaml
# Regex patterns
patterns:
  - label: emp_number
    regex: "\\bW[-\\s]?\\d{6,}\\b"
    confidence: 0.9

  - label: project_code
    regex: "\\bPROJ-[A-Z]{2}\\d{4}\\b"
    confidence: 0.85

# Keyword groups
keywords:
  - label: internal_projects
    terms: ["project phoenix", "operation nighthawk"]
    confidence: 0.8

# Disable built-in defaults you don't need
# disable_defaults:
#   - badge_number
#   - payroll_id
```

Built-in defaults (employee ID, badge number, payroll ID) run automatically unless disabled. User patterns merge on top.

## How Confidence Affects Scoring

Confidence scores are set per pattern and propagate into the risk score:

| Confidence | Score multiplier |
|------------|-----------------|
| ≥ 0.9 | 1.2× |
| 0.7–0.9 | 1.0× |
| < 0.7 | 0.8× |

High-confidence patterns (like `private_key` at 0.99) push scores higher than low-confidence heuristics (like `generic_secret` at 0.7).
