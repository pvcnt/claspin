from claspin.model.common import BaseModel
from claspin.model.variable import LabelValue
from claspin.plugins.interface import ListVariableData, ListVariablePlugin, QueryContext


class StaticListVariableAttrs(BaseModel):
    values: list[str]


class StaticListVariableSpec(BaseModel):
    values: list[LabelValue]


class StaticListVariablePlugin(ListVariablePlugin[StaticListVariableSpec]):
    kind = "StaticListVariable"

    def eval(self, props: dict) -> StaticListVariableSpec:
        attrs = StaticListVariableAttrs.model_validate(props)
        return StaticListVariableSpec(values=[LabelValue(value=v) for v in attrs.values])

    def fetch(self, spec: StaticListVariableSpec, ctx: QueryContext) -> ListVariableData:
        return ListVariableData(values=spec.values)
