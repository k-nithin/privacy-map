# Risk Scoring

Each asset and application receives a score from 0 to 100 with a mapped risk level. Scores are additive and every point has a traceable driver — no black-box results.

## Risk Levels

| Score | Level |
|-------|-------|
| 0–24 | Low |
| 25–49 | Medium |
| 50–69 | High |
| 70–100 | Critical |

## Asset Scoring

### Detection weights (base)

| Signal | Base points |
|--------|------------|
| PII detected | 25 |
| Secrets/credentials detected | 30 |
| Sensitive domain content | 15 |

Detection scores are **scaled by two factors** before being added:

**Match density** (how pervasive hits are within sampled content):

| Match rate | Multiplier |
|------------|-----------|
| > 10% | 1.4× |
| 2–10% | 1.0× |
| < 2% | 0.6× |

**Detector confidence**:

| Confidence | Multiplier |
|------------|-----------|
| ≥ 0.9 | 1.2× |
| 0.7–0.9 | 1.0× |
| < 0.7 | 0.8× |

Example: PII at 30% match rate and 0.95 confidence → `25 × 1.4 × 1.2 = 42 pts`

### Asset type bonuses (structural risk, not scaled)

| Asset type | Points |
|------------|--------|
| `prompt_logs` | +20 |
| `vector_table` | +15 |
| `training_data` | +10 |
| `transcripts` | +10 |

### Data size bonus

| Size | Points |
|------|--------|
| > 10 MB or > 10k rows | +10 |
| > 100 KB or > 100 rows | +5 |

### Sampling coverage warning

If less than 1% of a large asset was sampled, a warning is added to the drivers: the score may be conservative because most of the data was not examined.

## Application Scoring

Applications inherit risk from their dependencies:

| Signal | Points |
|--------|--------|
| Uses external model endpoint | +20 |
| PII found in a dependency | +20 |
| Secrets found in a dependency | +25 |
| Depends on a high/critical asset | +15 |
| Multiple high/critical dependencies | +10 |

## Example Drivers

The report includes drivers explaining each point addition:

```
- Secrets/credentials detected: 4 matches, 16.0% density, 95% confidence → +50
- PII detected: 14 matches, 28.0% density, 95% confidence → +42
- Asset is a prompt log store
- Large data asset (>10 MB / >10k rows)
- Warning: 0.5% of rows sampled — score may underestimate actual risk
```
