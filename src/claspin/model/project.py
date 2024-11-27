from typing import Literal

from claspin.model.common import BaseModel, Kind, Metadata


class Project(BaseModel):
    kind: Literal[Kind.project] = Kind.project
    metadata: Metadata


DEFAULT_PROJECT = Project(metadata=Metadata(name="default"))
