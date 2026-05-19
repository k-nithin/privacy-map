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
