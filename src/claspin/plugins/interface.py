from abc import ABC
from typing import Tuple, Type

from claspin.model.common import Plugin
from claspin.model.datasource import DatasourcePlugin
from claspin.model.query import TimeSeriesQueryPlugin
from claspin.model.variable import ListVariablePlugin


class Extension(ABC):
    name: str
    plugins: Tuple[Type[Plugin], ...]

    @property
    def datasource_plugins(self) -> Tuple[Type[DatasourcePlugin], ...]:
        return tuple(v for v in self.plugins if issubclass(v, DatasourcePlugin))

    @property
    def time_series_query_plugins(self) -> Tuple[Type[TimeSeriesQueryPlugin], ...]:
        return tuple(v for v in self.plugins if issubclass(v, TimeSeriesQueryPlugin))

    @property
    def list_variable_plugins(self) -> Tuple[Type[ListVariablePlugin], ...]:
        return tuple(v for v in self.plugins if issubclass(v, ListVariablePlugin))
