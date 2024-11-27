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

    def model_dump_yaml(self, exclude_unset: bool = False, indent: int | None = None) -> str:
        # jsonable_encoder ensures that the representation is identical to
        # the one provided by FastAPI.
        return yaml.dump(jsonable_encoder(self, exclude_unset=exclude_unset), indent=indent)


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


class Display(BaseModel):
    name: str | None = None
    description: str | None = None
    hidden: bool = False


class Plugin(BaseModel, ABC):
    @classmethod
    def kind(cls) -> str:
        return cls.__name__

    @classmethod
    def method_name(cls) -> str:
        return to_snake(cls.kind())
