from abc import ABC
from typing import Self

import yaml
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, computed_field, model_validator
from pydantic.alias_generators import to_camel, to_snake

NEGATIVE_INFINITY = float("-inf")
POSITIVE_INFINITY = float("+inf")

DEFAULT_PROJECT = "default"


class BaseModel(_BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Metadata(BaseModel):
    name: str
    project: str | None = None


class Display(BaseModel):
    name: str | None = None
    description: str | None = None
    hidden: bool = False


class Entity(BaseModel, ABC):
    metadata: Metadata

    @computed_field(alias="kind")
    @property
    def _kind(self) -> str:
        return self.kind()

    @classmethod
    def kind(cls) -> str:
        return cls.__name__

    @classmethod
    def namespaced(cls) -> bool:
        return cls.kind() != "Project"

    @model_validator(mode="after")
    def set_default_namespace(self) -> Self:
        if self.namespaced() and self.metadata.project is None:
            self.metadata.project = DEFAULT_PROJECT
        return self

    def model_dump_yaml(self, exclude_unset: bool = False, indent: int | None = None) -> str:
        # jsonable_encoder ensures that the representation is identical to
        # the one provided by FastAPI.
        return yaml.dump(jsonable_encoder(self, exclude_unset=exclude_unset), indent=indent)


class Plugin(BaseModel, ABC):
    @classmethod
    def kind(cls) -> str:
        return cls.__name__

    @classmethod
    def method_name(cls) -> str:
        return to_snake(cls.kind())
