from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import LiteralString

from pydantic import Field
from pydantic.alias_generators import to_snake

from claspin.database import Database
from claspin.model.common import BaseModel
from claspin.model.datasource import Datasource, DatasourceSelector
from claspin.model.variable import LabelValue


class Plugin[T: BaseModel](ABC):
    kind: LiteralString

    @property
    def method_name(self) -> str:
        return to_snake(self.kind)

    @abstractmethod
    def eval(self, props: dict) -> T:
        raise NotImplementedError()


class DatasourcePlugin[T: BaseModel](Plugin[T], ABC):
    def close(self, spec: T) -> None:
        pass


class PanelPlugin[T: BaseModel](Plugin[T], ABC):
    pass


class QueryContext:
    def __init__(
        self,
        start: datetime,
        end: datetime,
        suggested_step: timedelta,
        db: Database,
    ) -> None:
        self.start = start
        self.end = end
        self.suggested_step = suggested_step
        self.db = db

    def get_datasource(self, selector: DatasourceSelector) -> Datasource:
        for datasource in self.db.query(Datasource):
            if datasource.matches(selector):
                return datasource
        raise ValueError(f"No datasource matches {selector}")


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


class ListVariableData(BaseModel):
    values: list[LabelValue]


class TimeSeriesQueryPlugin[T: BaseModel](Plugin[T], ABC):
    @abstractmethod
    def fetch(self, spec: T, ctx: QueryContext) -> TimeSeriesData:
        raise NotImplementedError()


class ListVariablePlugin[T: BaseModel](Plugin[T], ABC):
    @abstractmethod
    def fetch(self, spec: T, ctx: QueryContext) -> ListVariableData:
        raise NotImplementedError()
