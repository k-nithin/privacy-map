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

"""Asset data model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Asset:
    asset_id: str
    asset_type: str  # table, vector_table, file, directory, prompt_logs, training_data, transcripts, documents
    store_type: str  # postgres, pgvector, filesystem
    location: str
    schema_info: dict[str, Any] = field(default_factory=dict)
    classification: list[str] = field(default_factory=list)
    sample_size: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "store_type": self.store_type,
            "location": self.location,
            "schema_info": self.schema_info,
            "classification": self.classification,
            "sample_size": self.sample_size,
            "metadata": self.metadata,
        }
