from abc import ABC
from typing import Literal

from claspin.model.common import BaseModel, Metadata, Plugin


class DatasourcePlugin(Plugin, ABC):
    async def close(self) -> None:
        pass


class DatasourcePluginModel[T: DatasourcePlugin](BaseModel):
    kind: str
    spec: T


class DatasourceSpec(BaseModel):
    plugin: DatasourcePluginModel


class Datasource(BaseModel):
    kind: Literal["Datasource"] = "Datasource"
    metadata: Metadata
    spec: DatasourceSpec
