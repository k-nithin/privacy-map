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

"""Tests for sensitivity detector."""

from aipbom.detectors.sensitivity import SensitivityDetector


def test_detect_hr():
    detector = SensitivityDetector()
    results = detector.detect("Employee salary review for Q4 compensation adjustment.")
    assert any(d.label == "hr" for d in results)


def test_detect_finance():
    detector = SensitivityDetector()
    results = detector.detect("Revenue forecast and balance sheet audit for fiscal year.")
    assert any(d.label == "finance" for d in results)


def test_detect_health():
    detector = SensitivityDetector()
    results = detector.detect("Patient diagnosis and treatment plan for medication review.")
    assert any(d.label == "health" for d in results)


def test_detect_legal():
    detector = SensitivityDetector()
    results = detector.detect("Attorney-client privileged communication regarding litigation settlement.")
    assert any(d.label == "legal" for d in results)


def test_no_sensitivity():
    detector = SensitivityDetector()
    results = detector.detect("The sun is shining and birds are singing.")
    assert results == []


def test_multiple_domains():
    detector = SensitivityDetector()
    text = "Employee salary bank account routing number patient diagnosis"
    results = detector.detect(text)
    labels = {d.label for d in results}
    assert "hr" in labels
    assert "finance" in labels
    assert "health" in labels
