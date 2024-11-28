from abc import ABC

from pydantic import computed_field

from claspin.model.common import BaseModel, Entity, Plugin


class DatasourcePlugin(Plugin, ABC):
    async def close(self) -> None:
        pass


class DatasourcePluginDefinition[T: DatasourcePlugin](BaseModel):
    spec: T

    @computed_field
    @property
    def kind(self) -> str:
        return self.spec.kind()


class DatasourceSpec(BaseModel):
    plugin: DatasourcePluginDefinition


class Datasource(Entity):
    spec: DatasourceSpec
