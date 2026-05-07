"""Postgres connector for structured tables."""

import logging

import psycopg2

from aipbom.connectors.base import BaseConnector
from aipbom.models import Asset

logger = logging.getLogger(__name__)

# Names that hint at AI-relevant asset types
ASSET_TYPE_HINTS = {
    "prompt_log": "prompt_logs",
    "prompt_logs": "prompt_logs",
    "messages": "prompt_logs",
    "chat_log": "prompt_logs",
    "training_data": "training_data",
    "train": "training_data",
    "embeddings": "vector_table",
    "transcripts": "transcripts",
    "transcript": "transcripts",
    "documents": "documents",
    "document": "documents",
}


def _infer_asset_type(table_name: str) -> str:
    name_lower = table_name.lower()
    for hint, asset_type in ASSET_TYPE_HINTS.items():
        if hint in name_lower:
            return asset_type
    return "table"


class PostgresConnector(BaseConnector):
    """Connector for Postgres databases."""

    def __init__(self, config: dict):
        super().__init__(config)
        conn_cfg = config.get("connection", {})
        self.conn = psycopg2.connect(
            host=conn_cfg.get("host", "localhost"),
            port=conn_cfg.get("port", 5432),
            dbname=conn_cfg.get("database", "postgres"),
            user=conn_cfg.get("user", "postgres"),
            password=conn_cfg.get("password", ""),
        )
        self.schemas = config.get("schemas", ["public"])

    def discover(self) -> list[Asset]:
        assets = []
        with self.conn.cursor() as cur:
            for schema in self.schemas:
                cur.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = %s AND table_type = 'BASE TABLE'",
                    (schema,),
                )
                for (table_name,) in cur.fetchall():
                    columns = self._get_columns(cur, schema, table_name)
                    asset_id = f"pg:{schema}.{table_name}"
                    asset = Asset(
                        asset_id=asset_id,
                        asset_type=_infer_asset_type(table_name),
                        store_type="postgres",
                        location=f"{schema}.{table_name}",
                        schema_info={"columns": columns},
                    )
                    assets.append(asset)
                    logger.info("Discovered postgres asset: %s", asset_id)
        return assets

    def sample(self, asset: Asset, max_rows: int = 100, max_chars: int = 10000) -> list[str]:
        table = asset.location
        samples = []
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table} LIMIT %s", (max_rows,))  # noqa: S608
            col_names = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                row_text = " ".join(
                    f"{col}={val}" for col, val in zip(col_names, row)
                    if val is not None
                )
                if row_text:
                    samples.append(row_text[:max_chars])
        return samples

    def _get_columns(self, cur, schema: str, table: str) -> dict[str, str]:
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (schema, table),
        )
        return {name: dtype for name, dtype in cur.fetchall()}

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
