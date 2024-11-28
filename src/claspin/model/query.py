from typing import Literal

from claspin.model.common import BaseModel, Entity


class TimeSeriesQueryPluginDefinition[T: BaseModel](BaseModel):
    kind: str
    spec: T


class TimeSeriesQuerySpec(BaseModel):
    plugin: TimeSeriesQueryPluginDefinition


class TimeSeriesQuery(BaseModel):
    kind: Literal["TimeSeriesQuery"] = "TimeSeriesQuery"
    spec: TimeSeriesQuerySpec


QuerySpec = TimeSeriesQuery


class Query(Entity):
    spec: QuerySpec
