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
