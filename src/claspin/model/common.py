from abc import ABC
from enum import StrEnum, unique
from typing import Any, Self

import yaml
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field, computed_field, model_validator
from pydantic.alias_generators import to_camel

NEGATIVE_INFINITY = float("-inf")
POSITIVE_INFINITY = float("+inf")

DEFAULT_PROJECT = "default"


class BaseModel(_BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @model_validator(mode="before")
    @classmethod
    def remove_none(cls, data: Any) -> Any:
        return _remove_none(data)


class JSONRef(BaseModel):
    ref: str = Field(alias="$ref")


class Metadata(BaseModel):
    name: str
    project: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class Display(BaseModel):
    name: str | None = None
    description: str | None = None
    hidden: bool = False


@unique
class Calculation(StrEnum):
    FIRST = "first"
    LAST = "last"
    FIRST_NUMBER = "first-number"
    LAST_NUMBER = "last-number"
    MEAN = "mean"
    SUM = "sum"
    MIN = "min"
    MAX = "max"


@unique
class Unit(StrEnum):
    # time units
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    # percent units
    PERCENT = "percent"
    PERCENT_DECIMAL = "percent-decimal"
    # decimal units
    DECIMAL = "decimal"
    # bytes units
    BYTES = "bytes"
    # throughput units
    BITS_PER_SEC = "bits/sec"
    BYTES_PER_SEC = "bytes/sec"
    COUNTS_PER_SEC = "counts/sec"
    EVENTS_PER_SEC = "events/sec"
    MESSAGES_PER_SEC = "messages/sec"
    OPS_PER_SEC = "ops/sec"
    PACKETS_PER_SEC = "packets/sec"
    READS_PER_SEC = "reads/sec"
    RECORDS_PER_SEC = "records/sec"
    REQUESTS_PER_SEC = "requests/sec"
    ROWS_PER_SEC = "rows/sec"
    WRITES_PER_SEC = "writes/sec"


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


def _remove_none(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _remove_none(v) for k, v in data.items() if v is not None}
    else:
        return data
