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
