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

"""Abstract base connector interface."""

from abc import ABC, abstractmethod

from aipbom.models import Asset


class BaseConnector(ABC):
    """Base interface for data source connectors."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def discover(self) -> list[Asset]:
        """Discover assets from the data source."""

    @abstractmethod
    def sample(self, asset: Asset, max_rows: int, max_chars: int) -> list[str]:
        """Sample text content from an asset. Returns list of text strings."""

    def close(self):
        """Clean up resources."""
