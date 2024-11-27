from abc import ABC, abstractmethod
from typing import Annotated, Literal, Self, Union

from pydantic import Field, computed_field, model_validator

from claspin.model.common import BaseModel, Display, Kind, Metadata, Plugin
from claspin.model.datasource import DatasourcePlugin
from claspin.model.project import DEFAULT_PROJECT
from claspin.model.query import QueryContext


class ListVariableData(BaseModel):
    values: dict[str, str]
    url: str | None = None


class ListVariablePlugin[T: DatasourcePlugin](Plugin, ABC):
    @abstractmethod
    async def fetch(self, ctx: QueryContext[T]) -> ListVariableData:
        raise NotImplementedError()


class ListVariablePluginDefinition[T: ListVariablePlugin](BaseModel):
    spec: T

    @computed_field
    @property
    def kind(self) -> str:
        return self.spec.kind()


class ListVariableSpec(BaseModel):
    plugin: ListVariablePluginDefinition
    name: str | None = None
    display: Display = Field(default_factory=Display)
    default_value: str | list[str] | None = None
    allow_all_value: bool = False
    allow_multiple: bool = False
    custom_all_value: str | None = None
    capturing_regexp: str | None = None


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


class Variable(BaseModel):
    kind: Literal[Kind.variable] = Kind.variable
    metadata: Metadata
    spec: VariableSpec

    @model_validator(mode="after")
    def set_default_namespace(self) -> Self:
        if self.metadata.project is None:
            self.metadata.project = DEFAULT_PROJECT.metadata.name
        return self
