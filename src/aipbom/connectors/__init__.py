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
