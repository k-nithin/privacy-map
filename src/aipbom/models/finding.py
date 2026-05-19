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

"""Finding data model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    finding_id: str
    subject_id: str
    subject_type: str  # asset or application
    severity: str  # low, medium, high, critical
    category: str  # pii, secrets, sensitivity, external_endpoint, vector_store
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "evidence": self.evidence,
        }
