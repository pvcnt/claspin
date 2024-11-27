from claspin.model.query import QueryContext
from claspin.model.variable import ListVariableData, ListVariablePlugin
from claspin.plugins.prometheus.datasource import PrometheusDatasource


class PrometheusLabelNamesVariable(ListVariablePlugin[PrometheusDatasource]):
    matchers: list[str] | None = None
    limit: int | None = None

    async def fetch(self, ctx: QueryContext[PrometheusDatasource]) -> ListVariableData:
        values = await ctx.datasource.client.label_names(
            start=ctx.start,
            end=ctx.end,
            match=self.matchers,
            limit=self.limit,
        )
        return ListVariableData(values={v: v for v in values if v != "__name__"})


class PrometheusLabelValuesVariable(ListVariablePlugin[PrometheusDatasource]):
    label_name: str
    matchers: list[str] | None = None
    limit: int | None = None

    async def fetch(self, ctx: QueryContext[PrometheusDatasource]) -> ListVariableData:
        values = await ctx.datasource.client.label_values(
            label=self.label_name,
            start=ctx.start,
            end=ctx.end,
            match=self.matchers,
            limit=self.limit,
        )
        return ListVariableData(values={v: v for v in values})
