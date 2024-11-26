from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Annotated, Literal, Sequence, Union

from pydantic import Field

from claspin.model.common import BaseModel, Metadata, Plugin
from claspin.model.datasource import DatasourcePlugin


class BaseColumn[T](BaseModel, ABC):
    name: str
    values: Sequence[T | None] = Field(default_factory=list)


class IntColumn(BaseColumn[int]):
    data_type: Literal["int"] = "int"


class FloatColumn(BaseColumn[float]):
    data_type: Literal["float"] = "float"


class StringColumn(BaseColumn[str]):
    data_type: Literal["string"] = "string"


class BoolColumn(BaseColumn[bool]):
    data_type: Literal["bool"] = "bool"


class TimeColumn(BaseColumn[datetime]):
    data_type: Literal["time"] = "time"


Column = Annotated[
    Union[IntColumn, FloatColumn, StringColumn, BoolColumn, TimeColumn],
    Field(discriminator="data_type"),
]


class DataFrame(BaseModel):
    columns: Sequence[Column]


class QueryContext(BaseModel):
    start: datetime
    end: datetime
    suggested_step: timedelta


class QueryPlugin[T: DatasourcePlugin](Plugin, ABC):
    @abstractmethod
    async def query(self, ds: T, ctx: QueryContext) -> DataFrame:
        raise NotImplementedError()


class QueryPluginModel[T: QueryPlugin](BaseModel):
    kind: str
    spec: T


class QuerySpec(BaseModel):
    plugin: QueryPluginModel


class Query(BaseModel):
    kind: Literal["Query"] = "Query"
    metadata: Metadata
    spec: QuerySpec
