from datetime import datetime, timedelta
from functools import cached_property

import pytz

from claspin.model.datasource import DatasourcePlugin
from claspin.model.query import LineData, QueryContext, TimeSeriesData, TimeSeriesQueryPlugin
from claspin.model.variable import ListVariableData, ListVariablePlugin
from claspin.plugins.interface import Extension
from claspin.plugins.prometheus.client import PrometheusClient


class PrometheusDatasource(DatasourcePlugin):
    url: str
    username: str | None = None
    password: str | None = None
    headers: dict[str, str] | None = None
    timeout: timedelta = timedelta(seconds=60)

    @cached_property
    def client(self) -> PrometheusClient:
        auth = (self.username, self.password) if self.username is not None and self.password is not None else None
        return PrometheusClient(
            url=self.url.rstrip("/"),
            auth=auth,
            headers=self.headers,
            timeout=self.timeout,
        )

    async def close(self) -> None:
        await self.client.close()


class PrometheusPromqlQuery(TimeSeriesQueryPlugin[PrometheusDatasource]):
    expr: str

    async def query(self, ctx: QueryContext[PrometheusDatasource]) -> TimeSeriesData:
        resp = await ctx.datasource.client.range_query(
            query=self.expr,
            start=ctx.start,
            end=ctx.end,
            step=ctx.suggested_step,
            timeout=ctx.datasource.timeout,
        )
        lines: list[LineData] = []
        for result in resp.result:
            if result.values:  # TODO: handle histograms
                metric = result.metric.pop("__name__")
                points = {datetime.fromtimestamp(value[0], tz=pytz.utc): float(value[1]) for value in result.values}
                lines.append(
                    LineData(metric=metric, points=points, labels=result.metric),
                )
        url = f"{ctx.datasource.url}/query?g0.expr={self.expr}"  # TODO: include time range
        return TimeSeriesData(lines=lines, step=ctx.suggested_step, url=url)


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


class PrometheusExtension(Extension):
    name = "prometheus"
    plugins = (
        PrometheusDatasource,
        PrometheusPromqlQuery,
        PrometheusLabelNamesVariable,
        PrometheusLabelValuesVariable,
    )
