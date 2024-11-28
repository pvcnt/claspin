from pathlib import Path

from claspin.config.loader import ConfigLoader
from claspin.config.parser import ConfigParser
from claspin.database import Database
from claspin.plugins import BUILTIN_PLUGINS
from claspin.workspace import Workspace


class Runtime:
    def __init__(self, root_dir: Path) -> None:
        self.workspace = Workspace(root_dir)
        self.db = Database()
        self.parser = ConfigParser(self.workspace)
        self.loader = ConfigLoader(self.db)

        for plugin in BUILTIN_PLUGINS:
            self.workspace.add_plugin(plugin)

    def eval_and_load(self) -> None:
        graph = self.parser.eval()
        self.loader.load(graph)
