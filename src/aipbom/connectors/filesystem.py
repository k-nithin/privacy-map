"""Filesystem connector for local files and directories."""

import logging
from pathlib import Path

from aipbom.connectors.base import BaseConnector
from aipbom.models import Asset

logger = logging.getLogger(__name__)

TEXT_EXTENSIONS = {".txt", ".json", ".csv", ".md", ".jsonl", ".yaml", ".yml", ".log", ".xml"}

ASSET_TYPE_HINTS = {
    "prompt": "prompt_logs",
    "chat": "prompt_logs",
    "chat_history": "prompt_logs",
    "conversation": "prompt_logs",
    "message": "prompt_logs",
    "training": "training_data",
    "train": "training_data",
    "transcript": "transcripts",
    "document": "documents",
    "embedding": "vector_table",
}


def _infer_asset_type_from_path(path: Path) -> str:
    name_lower = path.name.lower()
    for hint, asset_type in ASSET_TYPE_HINTS.items():
        if hint in name_lower:
            return asset_type
    if path.is_dir():
        return "directory"
    return "file"


class FilesystemConnector(BaseConnector):
    """Connector for local filesystem scanning."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.root_paths = [Path(p) for p in config.get("paths", [])]
        self.include_patterns = config.get("include_patterns", ["*"])
        self.exclude_patterns = config.get("exclude_patterns", [])

    def discover(self) -> list[Asset]:
        assets = []
        for root in self.root_paths:
            if not root.exists():
                logger.warning("Path does not exist: %s", root)
                continue

            if root.is_file():
                asset = self._file_to_asset(root)
                if asset:
                    assets.append(asset)
                continue

            # Discover directory itself
            assets.append(Asset(
                asset_id=f"fs:{root}",
                asset_type=_infer_asset_type_from_path(root),
                store_type="filesystem",
                location=str(root),
            ))

            # Discover files within
            for path in sorted(root.rglob("*")):
                if path.is_file() and self._should_include(path):
                    asset = self._file_to_asset(path)
                    if asset:
                        assets.append(asset)

        return assets

    def sample(self, asset: Asset, max_rows: int = 50, max_chars: int = 10000) -> list[str]:
        path = Path(asset.location)
        if path.is_file():
            return self._read_file(path, max_chars)
        if path.is_dir():
            return self._sample_directory(path, max_rows, max_chars)
        return []

    def _file_to_asset(self, path: Path) -> Asset | None:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            return None
        asset_id = f"fs:{path}"
        asset = Asset(
            asset_id=asset_id,
            asset_type=_infer_asset_type_from_path(path),
            store_type="filesystem",
            location=str(path),
            schema_info={"extension": path.suffix, "size_bytes": path.stat().st_size},
        )
        logger.info("Discovered filesystem asset: %s", asset_id)
        return asset

    def _read_file(self, path: Path, max_chars: int) -> list[str]:
        try:
            text = path.read_text(errors="replace")[:max_chars]
            return [text] if text.strip() else []
        except (OSError, UnicodeDecodeError) as e:
            logger.warning("Could not read %s: %s", path, e)
            return []

    def _sample_directory(self, directory: Path, max_files: int, max_chars: int) -> list[str]:
        samples = []
        count = 0
        for path in sorted(directory.rglob("*")):
            if count >= max_files:
                break
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                samples.extend(self._read_file(path, max_chars))
                count += 1
        return samples

    def _should_include(self, path: Path) -> bool:
        name = path.name
        for pattern in self.exclude_patterns:
            if path.match(pattern):
                return False
        if self.include_patterns == ["*"]:
            return True
        return any(path.match(p) for p in self.include_patterns)
