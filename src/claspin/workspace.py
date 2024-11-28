import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from claspin.database import Database
from claspin.plugins.interface import DatasourcePlugin, ListVariablePlugin, PanelPlugin, Plugin, TimeSeriesQueryPlugin

STAR_SUFFIX = ".star"
ABSOLUTE_PREFIX = "//"


@dataclass(frozen=True)
class ConfigFile:
    path: str
    content: str

    @property
    def label(self) -> str:
        return f"{ABSOLUTE_PREFIX}{self.path}"


class Workspace:
    def __init__(self, root_dir: Path) -> None:
        self._log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.root_dir = root_dir
        self.db = Database()
        self._plugins: list[Plugin] = []

    def add_plugin(self, plugin: Plugin) -> None:
        self._plugins.append(plugin)

    @property
    def datasource_plugins(self) -> Sequence[DatasourcePlugin]:
        return tuple(v for v in self._plugins if isinstance(v, DatasourcePlugin))

    @property
    def time_series_query_plugins(self) -> Sequence[TimeSeriesQueryPlugin]:
        return tuple(v for v in self._plugins if isinstance(v, TimeSeriesQueryPlugin))

    @property
    def list_variable_plugins(self) -> Sequence[ListVariablePlugin]:
        return tuple(v for v in self._plugins if isinstance(v, ListVariablePlugin))

    @property
    def panel_plugins(self) -> Sequence[PanelPlugin]:
        return tuple(v for v in self._plugins if isinstance(v, PanelPlugin))

    def resolve_file(self, s: str, base: ConfigFile | None = None) -> ConfigFile:
        if s.startswith(ABSOLUTE_PREFIX):
            path = self.root_dir.joinpath(s[len(ABSOLUTE_PREFIX) :])
            if self._is_config_file(path):
                return self._make_config_file(path)
        elif base is not None:
            path = self.root_dir.joinpath(base.path).parent.joinpath(s)
            if self._is_config_file(path):
                return self._make_config_file(path)
        raise ValueError(f"Cannot resolve label '{s}'")

    def iter_files(self) -> Iterable[ConfigFile]:
        return self._iter_files(self.root_dir)

    def _iter_files(self, path: Path) -> Iterable[ConfigFile]:
        for child in path.iterdir():
            if self._is_config_file(child):
                yield self._make_config_file(child)
            elif child.is_dir():
                yield from self._iter_files(child)

    def _is_config_file(self, path: Path) -> bool:
        return path.suffix == STAR_SUFFIX and path.is_file()

    def _make_config_file(self, path: Path):
        return ConfigFile(
            path=str(path.relative_to(self.root_dir)),
            content=path.read_text(),
        )
