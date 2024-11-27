from abc import ABC
from enum import StrEnum, unique

import yaml
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel, to_snake

NEGATIVE_INFINITY = float("-inf")
POSITIVE_INFINITY = float("+inf")


class BaseModel(_BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    def model_dump_yaml(self, indent: int | None = None) -> str:
        # jsonable_encoder ensures that the representation is identical to
        # the one provided by FastAPI.
        return yaml.dump(jsonable_encoder(self), indent=indent)


class Attrs(BaseModel, ABC):
    pass


@unique
class Kind(StrEnum):
    project = "Project"
    datasource = "Datasource"
    variable = "Variable"
    query = "Query"

    @property
    def namespaced(self) -> bool:
        return self != Kind.project


class Metadata(BaseModel):
    name: str
    project: str | None = None


class Plugin(Attrs, ABC):
    @classmethod
    def kind(cls) -> str:
        return cls.__name__

    @classmethod
    def method_name(cls) -> str:
        return to_snake(cls.kind())
