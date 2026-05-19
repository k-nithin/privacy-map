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

"""Abstract base detector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Detection:
    """A single detection result."""
    detector_type: str  # pii, secrets, sensitivity
    label: str  # email, phone, api_key, hr, finance, etc.
    confidence: float  # 0.0 to 1.0
    matched_text: str = ""  # masked or truncated snippet


class BaseDetector(ABC):
    """Base interface for content detectors."""

    @property
    @abstractmethod
    def detector_type(self) -> str:
        """Return detector category name."""

    @abstractmethod
    def detect(self, text: str) -> list[Detection]:
        """Run detection on a text sample. Returns list of Detections."""
