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

"""Application data model."""

from dataclasses import dataclass, field


@dataclass
class Application:
    app_id: str
    app_type: str  # chatbot, copilot, classifier, summarizer, agent
    model_provider: str
    model_name: str
    external_endpoint: str | None = None
    declared_dependencies: list[str] = field(default_factory=list)

    @property
    def endpoint_type(self) -> str:
        return "external" if self.external_endpoint else "local"

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "app_type": self.app_type,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "endpoint_type": self.endpoint_type,
            "external_endpoint": self.external_endpoint,
            "declared_dependencies": self.declared_dependencies,
        }
