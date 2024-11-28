from pydantic import Field

from claspin.model.common import BaseModel, Display, Entity
from claspin.model.query import QuerySpec


class PanelPluginDefinition[T: BaseModel](BaseModel):
    kind: str
    spec: T


class PanelSpec(BaseModel):
    plugin: PanelPluginDefinition
    display: Display = Field(default_factory=Display)
    queries: list[QuerySpec] = Field(default_factory=list)


class Panel(Entity):
    spec: PanelSpec
