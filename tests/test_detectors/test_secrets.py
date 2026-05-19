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

"""Tests for secrets detector."""

from aipbom.detectors.secrets import SecretsDetector


def test_detect_aws_key():
    detector = SecretsDetector()
    results = detector.detect("aws key: AKIAIOSFODNN7EXAMPLE")
    assert any(d.label == "aws_access_key" for d in results)


def test_detect_bearer_token():
    detector = SecretsDetector()
    results = detector.detect("Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123def456")
    assert any(d.label == "bearer_token" for d in results)


def test_detect_generic_api_key():
    detector = SecretsDetector()
    results = detector.detect("api_key: sk_live_abcdefghij1234567890")
    assert any(d.label == "generic_api_key" for d in results)


def test_detect_private_key():
    detector = SecretsDetector()
    results = detector.detect("-----BEGIN RSA PRIVATE KEY-----\nMIIE...")
    assert any(d.label == "private_key" for d in results)


def test_detect_openai_key():
    detector = SecretsDetector()
    results = detector.detect("OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz1234567890")
    assert any(d.label == "openai_api_key" for d in results)


def test_detect_anthropic_key():
    detector = SecretsDetector()
    results = detector.detect("key: sk-ant-api03-abcdefghijklmnopqrstuvwxyz")
    assert any(d.label == "anthropic_api_key" for d in results)


def test_no_secrets():
    detector = SecretsDetector()
    results = detector.detect("This is just a normal paragraph about cats.")
    assert results == []
