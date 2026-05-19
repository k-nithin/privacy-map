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

"""Map applications to discovered assets based on declared dependencies."""

import logging
from dataclasses import dataclass

from aipbom.models import Application, Asset

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents a link between an application and an asset."""
    app_id: str
    asset_id: str
    relationship_type: str = "depends_on"

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "asset_id": self.asset_id,
            "relationship_type": self.relationship_type,
        }


def map_applications(
    applications: list[Application],
    assets: list[Asset],
) -> list[Relationship]:
    """Match declared dependencies to discovered assets.

    Matching logic:
    - Exact match on asset_id
    - Partial match on asset location (contains dependency string)
    """
    relationships = []
    asset_index = {a.asset_id: a for a in assets}
    # Also index by location for flexible matching
    location_index: dict[str, Asset] = {}
    for a in assets:
        location_index[a.location.lower()] = a

    for app in applications:
        for dep in app.declared_dependencies:
            matched_asset = _resolve_dependency(dep, asset_index, location_index)
            if matched_asset:
                relationships.append(Relationship(
                    app_id=app.app_id,
                    asset_id=matched_asset.asset_id,
                ))
                logger.info("Mapped %s -> %s", app.app_id, matched_asset.asset_id)
            else:
                logger.warning(
                    "Unresolved dependency for app %s: %s", app.app_id, dep
                )

    return relationships


def _resolve_dependency(
    dep: str,
    asset_index: dict[str, Asset],
    location_index: dict[str, Asset],
) -> Asset | None:
    """Try to resolve a dependency string to a discovered asset."""
    # Exact match on asset_id
    if dep in asset_index:
        return asset_index[dep]

    # Match by location
    dep_lower = dep.lower()
    if dep_lower in location_index:
        return location_index[dep_lower]

    # Partial match: check if dep is contained in any location
    for loc, asset in location_index.items():
        if dep_lower in loc or loc in dep_lower:
            return asset

    return None
