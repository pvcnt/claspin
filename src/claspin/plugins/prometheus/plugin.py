from datetime import datetime, timedelta
from functools import cached_property

import pytz

from claspin.model.datasource import DatasourcePlugin
from claspin.model.query import (
    DataFrame,
    FloatColumn,
    QueryContext,
    QueryPlugin,
    StringColumn,
    TimeColumn,
)
from claspin.plugins.prometheus.client import PrometheusClient


class PrometheusDatasource(DatasourcePlugin):
    url: str
    username: str | None = None
    password: str | None = None
    headers: dict[str, str] | None = None
    timeout: timedelta = timedelta(seconds=60)

    @cached_property
    def client(self) -> PrometheusClient:
        auth = (
            (self.username, self.password)
            if self.username is not None and self.password is not None
            else None
        )
        return PrometheusClient(
            url=self.url.rstrip("/"),
            auth=auth,
            headers=self.headers,
            timeout=self.timeout,
        )

    async def close(self) -> None:
        await self.client.close()


class PrometheusPromqlQuery(QueryPlugin[PrometheusDatasource]):
    expr: str

    async def query(self, ds: PrometheusDatasource, ctx: QueryContext) -> DataFrame:
        resp = await ds.client.range_query(
            query=self.expr,
            start=ctx.start,
            end=ctx.end,
            step=ctx.suggested_step,
            timeout=ds.timeout,
        )

        times: list[datetime] = []
        values: list[float] = []
        metrics: list[str] = []
        labels: dict[str, list[str | None]] = {
            v: [] for res in resp.result for v in res.metric if v != "__name__"
        }

        for result in resp.result:
            metric = result.metric["__name__"]
            if result.values:
                for value in result.values:
                    times.append(datetime.fromtimestamp(value[0], tz=pytz.utc))
                    values.append(float(value[1]))
                    metrics.append(metric)
                    for k in labels.keys():
                        labels[k].append(result.metric.get(k))

        return DataFrame(
            columns=[
                TimeColumn(name="time", values=times),
                FloatColumn(name="value", values=values),
                StringColumn(name="metric", values=metrics),
            ]
            + [StringColumn(name=f"label.{k}", values=v) for k, v in labels]
        )


class PrometheusLabelNamesQuery(QueryPlugin[PrometheusDatasource]):
    metric: str | None = None
    limit: int | None = None

    async def query(self, ds: PrometheusDatasource, ctx: QueryContext) -> DataFrame:
        label_names = await ds.client.label_names(
            start=ctx.start,
            end=ctx.end,
            match=self.metric,
            limit=self.limit,
        )
        values = [v for v in label_names if v != "__name__"]
        return DataFrame(columns=[StringColumn(name="value", values=values)])


class PrometheusLabelValuesQuery(QueryPlugin[PrometheusDatasource]):
    label: str
    metric: str | None = None
    limit: int | None = None

    async def query(self, ds: PrometheusDatasource, ctx: QueryContext) -> DataFrame:
        label_values = await ds.client.label_values(
            label=self.label,
            start=ctx.start,
            end=ctx.end,
            match=self.metric,
            limit=self.limit,
        )
        return DataFrame(columns=[StringColumn(name="value", values=label_values)])


class PrometheusMetricQuery(QueryPlugin[PrometheusDatasource]):
    metric: str | None = None
    limit: int | None = None

    async def query(self, ds: PrometheusDatasource, ctx: QueryContext) -> DataFrame:
        label_values = await ds.client.label_values(
            label="__name__",
            start=ctx.start,
            end=ctx.end,
            match=self.metric,
            limit=self.limit,
        )
        return DataFrame(columns=[StringColumn(name="value", values=label_values)])
