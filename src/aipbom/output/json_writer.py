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

"""JSON output writers for assets, findings, and PBOM."""

import json
from pathlib import Path

from aipbom.models import Asset, Application, Finding, RiskSummary
from aipbom.mapping.app_mapper import Relationship


def write_assets(assets: list[Asset], output_dir: Path) -> Path:
    path = output_dir / "assets.json"
    data = [a.to_dict() for a in assets]
    path.write_text(json.dumps(data, indent=2))
    return path


def write_findings(findings: list[Finding], output_dir: Path) -> Path:
    path = output_dir / "findings.json"
    data = [f.to_dict() for f in findings]
    path.write_text(json.dumps(data, indent=2))
    return path


def write_pbom(
    assets: list[Asset],
    applications: list[Application],
    relationships: list[Relationship],
    findings: list[Finding],
    asset_risks: list[RiskSummary],
    app_risks: list[RiskSummary],
    output_dir: Path,
) -> Path:
    """Write the complete PBOM JSON artifact."""
    path = output_dir / "pbom.json"
    pbom = {
        "version": "0.1.0",
        "assets": [a.to_dict() for a in assets],
        "applications": [a.to_dict() for a in applications],
        "relationships": [r.to_dict() for r in relationships],
        "findings": [f.to_dict() for f in findings],
        "risk_summaries": {
            "assets": [r.to_dict() for r in asset_risks],
            "applications": [r.to_dict() for r in app_risks],
        },
    }
    path.write_text(json.dumps(pbom, indent=2))
    return path
