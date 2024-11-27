from abc import ABC
from typing import Literal, Self

from pydantic import computed_field, model_validator

from claspin.model.common import BaseModel, Kind, Metadata, Plugin
from claspin.model.project import DEFAULT_PROJECT


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


class Datasource(BaseModel):
    kind: Literal[Kind.datasource] = Kind.datasource
    metadata: Metadata
    spec: DatasourceSpec

    @model_validator(mode="after")
    def set_default_namespace(self) -> Self:
        if self.metadata.project is None:
            self.metadata.project = DEFAULT_PROJECT.metadata.name
        return self
