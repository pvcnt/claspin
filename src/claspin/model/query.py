from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import Field, computed_field, model_validator

from claspin.model.common import BaseModel, Kind, Metadata, Plugin
from claspin.model.datasource import DatasourcePlugin
from claspin.model.project import DEFAULT_PROJECT


class QueryContext[T: DatasourcePlugin](BaseModel):
    start: datetime
    end: datetime
    suggested_step: timedelta
    datasource: T


class LineData(BaseModel):
    metric: str
    points: dict[datetime, float]
    labels: dict[str, str] = Field(default_factory=dict)

    @property
    def title(self) -> str:
        labels = "{" + ", ".join(f"{k}={v}" for k, v in self.labels.items()) + "}" if self.labels else ""
        return self.metric + labels


class TimeSeriesData(BaseModel):
    lines: list[LineData]
    step: timedelta
    url: str | None = None


class TimeSeriesQueryPlugin[T: DatasourcePlugin](Plugin, ABC):
    @abstractmethod
    async def query(self, ctx: QueryContext[T]) -> TimeSeriesData:
        raise NotImplementedError()


class TimeSeriesQueryPluginDefinition[T: TimeSeriesQueryPlugin](BaseModel):
    spec: T

    @computed_field
    @property
    def kind(self) -> str:
        return self.spec.kind()


class TimeSeriesQuerySpec(BaseModel):
    plugin: TimeSeriesQueryPluginDefinition


class TimeSeriesQuery(BaseModel):
    kind: Literal["TimeSeriesQuery"] = "TimeSeriesQuery"
    spec: TimeSeriesQuerySpec


QuerySpec = TimeSeriesQuery


class Query(BaseModel):
    kind: Literal[Kind.query] = Kind.query
    metadata: Metadata
    spec: QuerySpec

    @model_validator(mode="after")
    def set_default_namespace(self) -> Self:
        if self.metadata.project is None:
            self.metadata.project = DEFAULT_PROJECT.metadata.name
        return self
