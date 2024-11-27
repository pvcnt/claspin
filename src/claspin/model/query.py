from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Literal

from pydantic import Field, computed_field

from claspin.model.common import BaseModel, Metadata, Plugin
from claspin.model.datasource import DatasourcePlugin


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
    kind: Literal["Query"] = "Query"
    metadata: Metadata
    spec: QuerySpec
