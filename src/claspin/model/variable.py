from enum import StrEnum, unique
from typing import Annotated, Literal, Union

from pydantic import Field

from claspin.model.common import BaseModel, Display, Entity


class LabelValue(BaseModel):
    value: str
    label: str | None = None


class ListVariablePluginDefinition[T: BaseModel](BaseModel):
    kind: str
    spec: T


@unique
class VariableSort(StrEnum):
    NONE = "none"
    ALPHABETICAL_ASC = "alphabetical-asc"
    ALPHABETICAL_DESC = "alphabetical-desc"
    NUMERICAL_ASC = "numerical-asc"
    NUMERICAL_DESC = "numerical-desc"
    ALPHABETICAL_CI_ASC = "alphabetical-ci-asc"
    ALPHABETICAL_CI_DESC = "alphabetical-ci-desc"


class ListVariableSpec(BaseModel):
    plugin: ListVariablePluginDefinition
    name: str | None = None
    display: Display = Field(default_factory=Display)
    default_value: str | list[str] | None = None
    allow_all_value: bool = False
    allow_multiple: bool = False
    custom_all_value: str | None = None
    capturing_regexp: str | None = None
    sort: VariableSort = VariableSort.NONE


class ListVariable(BaseModel):
    kind: Literal["ListVariable"] = "ListVariable"
    spec: ListVariableSpec


class TextVariableSpec(BaseModel):
    value: str
    name: str | None = None
    display: Display = Field(default_factory=Display)
    constant: bool = False


class TextVariable(BaseModel):
    kind: Literal["TextVariable"] = "TextVariable"
    spec: TextVariableSpec


VariableSpec = Annotated[
    Union[TextVariable, ListVariable],
    Field(discriminator="kind"),
]


class Variable(Entity):
    spec: VariableSpec
