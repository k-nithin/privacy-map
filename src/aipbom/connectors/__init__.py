"""Data source connectors."""

from aipbom.connectors.postgres import PostgresConnector
from aipbom.connectors.pgvector import PgvectorConnector
from aipbom.connectors.filesystem import FilesystemConnector

CONNECTOR_REGISTRY: dict[str, type] = {
    "postgres": PostgresConnector,
    "pgvector": PgvectorConnector,
    "filesystem": FilesystemConnector,
}


def get_connector(source_config: dict):
    """Instantiate a connector from a data source config block."""
    connector_type = source_config["type"]
    cls = CONNECTOR_REGISTRY.get(connector_type)
    if cls is None:
        raise ValueError(f"Unknown connector type: {connector_type}")
    return cls(source_config)
