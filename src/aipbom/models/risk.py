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

"""Risk summary data model."""

from dataclasses import dataclass, field


@dataclass
class RiskSummary:
    subject_id: str
    subject_type: str  # asset or application
    risk_score: int
    risk_level: str  # low, medium, high, critical
    drivers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "drivers": self.drivers,
        }
