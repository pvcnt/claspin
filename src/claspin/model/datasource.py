from abc import ABC

from claspin.model.common import BaseModel, Entity


class DatasourceSelector(BaseModel, ABC):
    kind: str
    name: str | None = None


class DatasourcePluginDefinition[T: BaseModel](BaseModel):
    kind: str
    spec: T


class DatasourceSpec(BaseModel):
    plugin: DatasourcePluginDefinition


class Datasource(Entity):
    spec: DatasourceSpec

    def matches(self, selector: DatasourceSelector) -> bool:
        return self.kind() == selector.kind and (selector.name is None or selector.name == self.metadata.name)
