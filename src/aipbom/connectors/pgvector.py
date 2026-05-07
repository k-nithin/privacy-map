"""pgvector connector for vector tables in Postgres."""

import logging

import psycopg2

from aipbom.connectors.base import BaseConnector
from aipbom.models import Asset

logger = logging.getLogger(__name__)


class PgvectorConnector(BaseConnector):
    """Connector for pgvector tables (vector columns in Postgres)."""

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
        """Detect tables containing vector(n) columns."""
        assets = []
        with self.conn.cursor() as cur:
            for schema in self.schemas:
                # Find columns with vector type (pgvector extension)
                cur.execute(
                    "SELECT table_name, column_name, udt_name "
                    "FROM information_schema.columns "
                    "WHERE table_schema = %s AND udt_name = 'vector'",
                    (schema,),
                )
                vector_tables: dict[str, list[str]] = {}
                for table_name, col_name, _ in cur.fetchall():
                    vector_tables.setdefault(table_name, []).append(col_name)

                for table_name, vec_cols in vector_tables.items():
                    all_columns = self._get_columns(cur, schema, table_name)
                    metadata_cols = [
                        c for c in all_columns if c not in vec_cols
                    ]
                    asset_id = f"pgvec:{schema}.{table_name}"
                    asset = Asset(
                        asset_id=asset_id,
                        asset_type="vector_table",
                        store_type="pgvector",
                        location=f"{schema}.{table_name}",
                        schema_info={
                            "columns": all_columns,
                            "vector_columns": vec_cols,
                            "metadata_columns": metadata_cols,
                        },
                    )
                    assets.append(asset)
                    logger.info("Discovered pgvector asset: %s", asset_id)
        return assets

    def sample(self, asset: Asset, max_rows: int = 100, max_chars: int = 10000) -> list[str]:
        """Sample metadata (non-vector) columns from vector tables."""
        table = asset.location
        metadata_cols = asset.schema_info.get("metadata_columns", [])
        if not metadata_cols:
            return []

        col_list = ", ".join(metadata_cols)
        samples = []
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT {col_list} FROM {table} LIMIT %s", (max_rows,))  # noqa: S608
            for row in cur.fetchall():
                row_text = " ".join(
                    f"{col}={val}" for col, val in zip(metadata_cols, row)
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
