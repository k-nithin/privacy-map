"""Sensitivity domain classifier using keyword dictionaries."""

from aipbom.detectors.base import BaseDetector, Detection

# Domain keyword dictionaries
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "hr": [
        "employee", "salary", "compensation", "termination", "performance review",
        "hiring", "candidate", "resume", "onboarding", "payroll", "benefits",
        "leave", "pto", "disciplinary", "promotion", "demotion",
    ],
    "finance": [
        "revenue", "profit", "loss", "balance sheet", "invoice", "transaction",
        "bank account", "credit card", "routing number", "iban", "tax return",
        "audit", "budget", "forecast", "accounts payable", "accounts receivable",
    ],
    "health": [
        "patient", "diagnosis", "treatment", "prescription", "medical record",
        "hipaa", "insurance claim", "health condition", "symptoms", "lab results",
        "blood pressure", "allergies", "medication", "physician", "clinical",
    ],
    "legal": [
        "attorney", "litigation", "settlement", "contract", "nda",
        "confidential", "privileged", "deposition", "subpoena", "compliance",
        "regulatory", "lawsuit", "indemnification", "liability", "counsel",
    ],
    "customer_support": [
        "ticket", "complaint", "refund", "escalation", "customer feedback",
        "support request", "issue resolution", "sla", "satisfaction score",
        "churn", "retention", "helpdesk", "case number",
    ],
}


class SensitivityDetector(BaseDetector):
    """Keyword-based sensitivity domain classifier."""

    @property
    def detector_type(self) -> str:
        return "sensitivity"

    def detect(self, text: str) -> list[Detection]:
        detections = []
        text_lower = text.lower()

        for domain, keywords in DOMAIN_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                confidence = min(0.5 + 0.1 * len(matches), 1.0)
                detections.append(Detection(
                    detector_type=self.detector_type,
                    label=domain,
                    confidence=confidence,
                    matched_text=f"matched {len(matches)} keywords",
                ))

        return detections
