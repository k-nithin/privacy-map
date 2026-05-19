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

"""Tests for PII detector."""

from aipbom.detectors.pii import PiiDetector


def test_detect_email():
    detector = PiiDetector()
    results = detector.detect("Contact us at user@example.com for info.")
    assert any(d.label == "email" for d in results)


def test_detect_phone():
    detector = PiiDetector()
    results = detector.detect("Call me at (555) 123-4567 today.")
    assert any(d.label == "phone" for d in results)


def test_detect_ssn():
    detector = PiiDetector()
    results = detector.detect("SSN: 123-45-6789 on file.")
    assert any(d.label == "ssn" for d in results)


def test_detect_customer_id():
    detector = PiiDetector()
    results = detector.detect("customer_id: CUST12345 assigned.")
    assert any(d.label == "customer_id" for d in results)


def test_no_pii():
    detector = PiiDetector()
    results = detector.detect("The weather is sunny today.")
    assert results == []


def test_masking():
    detector = PiiDetector()
    results = detector.detect("Email: test@example.com")
    for d in results:
        assert "***" in d.matched_text
