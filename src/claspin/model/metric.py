from enum import StrEnum, auto
from typing import Optional, Union

from pydantic import Field

from claspin.model.common import (
    NEGATIVE_INFINITY,
    POSITIVE_INFINITY,
    ClaspinModel,
    ClaspinObject,
    ObjectRef,
)


class Aggregation(StrEnum):
    AVG = auto()
    SUM = auto()
    MIN = auto()
    MAX = auto()
    COUNT = auto()
    STDDEV = auto()
    P50 = auto()
    P75 = auto()
    P90 = auto()
    P95 = auto()
    P99 = auto()
    P999 = auto()


class Attribute(ClaspinModel):
    name: str
    column: Optional[str] = None


class Query(ClaspinModel):
    expr: str
    service: str
    attrs: list[Attribute] = Field(default_factory=list)
    agg: Aggregation = Aggregation.AVG
    unit: Optional[str] = None
    lower_bound: float = NEGATIVE_INFINITY
    upper_bound: float = POSITIVE_INFINITY


class WhereClause(ClaspinModel):
    attr: str
    value: str


class RatioComponent(ClaspinModel):
    metric: ObjectRef
    where: list[WhereClause] = Field(default_factory=list)


class Ratio(ClaspinModel):
    numerator: RatioComponent
    denominator: RatioComponent


class Level(StrEnum):
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    CRITICAL = auto()


class TimeUnit(StrEnum):
    SECONDS = auto()
    MINUTES = auto()
    HOURS = auto()
    DAYS = auto()


class TimeWindow(ClaspinModel):
    length: int
    unit: TimeUnit


class AlertRule(ClaspinModel):
    value: float
    level: Level
    trigger_after: Optional[TimeWindow] = None


class Alert(ClaspinModel):
    name: str
    base: float = NEGATIVE_INFINITY
    rules: list[AlertRule] = Field(default_factory=list)


class MetricSpec(ClaspinModel):
    # one-of:
    query: Optional[Query] = None
    ratio: Optional[Ratio] = None

    fill_na: Optional[float] = None
    alerts: list[Alert] = Field(default_factory=list)
    measure: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    owner: Union[str, list[str]] = Field(default_factory=list)


class Metric(ClaspinObject):
    spec: MetricSpec
