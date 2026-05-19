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

"""Tests for data models."""

from aipbom.models import Asset, Application, Finding, RiskSummary


def test_asset_to_dict():
    asset = Asset(
        asset_id="pg:public.users",
        asset_type="table",
        store_type="postgres",
        location="public.users",
    )
    d = asset.to_dict()
    assert d["asset_id"] == "pg:public.users"
    assert d["asset_type"] == "table"


def test_application_endpoint_type():
    app = Application(
        app_id="test",
        app_type="chatbot",
        model_provider="openai",
        model_name="gpt-4",
        external_endpoint="https://api.openai.com",
    )
    assert app.endpoint_type == "external"

    local_app = Application(
        app_id="local",
        app_type="summarizer",
        model_provider="local",
        model_name="llama",
    )
    assert local_app.endpoint_type == "local"


def test_finding_to_dict():
    f = Finding(
        finding_id="F-001",
        subject_id="asset-1",
        subject_type="asset",
        severity="high",
        category="pii",
        description="PII found",
        evidence={"match_count": 5},
    )
    d = f.to_dict()
    assert d["severity"] == "high"
    assert d["evidence"]["match_count"] == 5


def test_risk_summary_to_dict():
    r = RiskSummary(
        subject_id="asset-1",
        subject_type="asset",
        risk_score=55,
        risk_level="high",
        drivers=["PII detected"],
    )
    d = r.to_dict()
    assert d["risk_score"] == 55
    assert d["risk_level"] == "high"
