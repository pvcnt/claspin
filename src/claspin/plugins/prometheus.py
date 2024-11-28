from abc import ABC
from datetime import datetime, timedelta
from functools import cached_property
from typing import Sequence, Tuple, Union, cast

import httpx
import pytz

from claspin.model.common import BaseModel
from claspin.model.datasource import DatasourceSelector
from claspin.model.variable import LabelValue
from claspin.plugins.interface import (
    DatasourcePlugin,
    LineData,
    ListVariableData,
    ListVariablePlugin,
    QueryContext,
    TimeSeriesData,
    TimeSeriesQueryPlugin,
)


class Histogram(BaseModel):
    count: str
    sum: str
    buckets: list[Tuple[int, str, str, str]]


class RangeVector(BaseModel):
    metric: dict[str, str]
    values: list[Tuple[float, str]] | None = None
    histograms: list[Tuple[float, Histogram]] | None = None


class RangeQueryData(BaseModel):
    result: list[RangeVector]


class RangeQueryResponse(BaseModel):
    data: RangeQueryData


class LabelResponse(BaseModel):
    data: list[str]


class PrometheusClient:
    def __init__(
        self,
        url: str,
        auth: Tuple[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: timedelta | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=url,
            headers=headers,
            auth=auth,
            timeout=timeout.total_seconds() if timeout is not None else None,
        )

    def range_query(
        self,
        query: str,
        start: datetime,
        end: datetime,
        step: timedelta,
        timeout: timedelta | None = None,
    ) -> RangeQueryData:
        params = {
            "query": query,
            "start": str(start.timestamp()),
            "end": str(end.timestamp()),
            "step": str(step.total_seconds()),
        }
        if timeout is not None:
            params["timeout"] = self._get_duration(timeout)
        # Prefer using POST in case there is a long expression.
        resp = self._client.post(
            "/api/v1/query_range",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=params,
        )
        resp.raise_for_status()
        return RangeQueryResponse.model_validate_json(resp.read()).data

    def label_names(
        self,
        start: datetime,
        end: datetime,
        match: list[str] | None = None,
        limit: int | None = None,
    ) -> list[str]:
        params: dict[str, Union[str, Sequence[str]]] = {
            "start": str(start.timestamp()),
            "end": str(end.timestamp()),
        }
        if match is not None:
            params["match"] = match
        if limit is not None:
            params["limit"] = str(limit)
        resp = self._client.get("/api/v1/labels", params=params)
        resp.raise_for_status()
        return LabelResponse.model_validate_json(resp.read()).data

    def label_values(
        self,
        label: str,
        start: datetime,
        end: datetime,
        match: list[str] | None = None,
        limit: int | None = None,
    ) -> list[str]:
        params: dict[str, Union[str, Sequence[str]]] = {
            "start": str(start.timestamp()),
            "end": str(end.timestamp()),
        }
        if match is not None:
            params["match"] = match
        if limit is not None:
            params["limit"] = str(limit)
        resp = self._client.get(f"/api/v1/label/{label}/values", params=params)
        resp.raise_for_status()
        return LabelResponse.model_validate_json(resp.read()).data

    def close(self) -> None:
        self._client.close()

    def _get_duration(self, d: timedelta) -> str:
        return f"{int(d.total_seconds() * 1000)}ms"


class PrometheusDatasourceAttrs(BaseModel):
    url: str
    headers: dict[str, str] | None = None
    timeout: timedelta = timedelta(seconds=60)


class PrometheusDatasourceSpec(BaseModel):
    url: str
    headers: dict[str, str] | None = None
    timeout: timedelta

    @cached_property
    def client(self) -> PrometheusClient:
        return PrometheusClient(
            url=self.url.rstrip("/"),
            headers=self.headers,
            timeout=self.timeout,
        )


class PrometheusDatasourcePlugin(DatasourcePlugin[PrometheusDatasourceSpec]):
    kind = "PrometheusDatasource"

    def eval(self, props: dict) -> PrometheusDatasourceSpec:
        attrs = PrometheusDatasourceAttrs.model_validate(props)
        return PrometheusDatasourceSpec(
            url=attrs.url,
            headers=attrs.headers,
            timeout=attrs.timeout,
        )

    def close(self, spec: PrometheusDatasourceSpec) -> None:
        spec.client.close()


class PrometheusDatasourceSelector(DatasourceSelector):
    kind: str = PrometheusDatasourcePlugin.kind


class PrometheusPlugin(ABC):
    def get_datasource(self, selector: PrometheusDatasourceSelector, ctx: QueryContext) -> PrometheusDatasourceSpec:
        return cast(PrometheusDatasourceSpec, ctx.get_datasource(selector).spec.plugin.kind)


class PrometheusPromqlQueryAttrs(BaseModel):
    datasource: str | None = None
    query: str


class PrometheusPromqlQuerySpec(BaseModel):
    datasource: PrometheusDatasourceSelector
    query: str


class PrometheusPromqlQueryPlugin(TimeSeriesQueryPlugin[PrometheusPromqlQuerySpec], PrometheusPlugin):
    kind = "PrometheusPromqlQuery"

    def eval(self, props: dict) -> PrometheusPromqlQuerySpec:
        attrs = PrometheusPromqlQueryAttrs.model_validate(props)
        return PrometheusPromqlQuerySpec(
            datasource=PrometheusDatasourceSelector(name=attrs.datasource),
            query=attrs.query,
        )

    def fetch(self, spec: PrometheusPromqlQuerySpec, ctx: QueryContext) -> TimeSeriesData:
        datasource = self.get_datasource(spec.datasource, ctx)
        resp = datasource.client.range_query(
            query=spec.query,
            start=ctx.start,
            end=ctx.end,
            step=ctx.suggested_step,
            timeout=datasource.timeout,
        )
        lines: list[LineData] = []
        for result in resp.result:
            if result.values:  # TODO: handle histograms
                metric = result.metric.pop("__name__")
                points = {datetime.fromtimestamp(value[0], tz=pytz.utc): float(value[1]) for value in result.values}
                lines.append(
                    LineData(metric=metric, points=points, labels=result.metric),
                )
        url = f"{datasource.url}/query?g0.expr={spec.query}"  # TODO: include time range
        return TimeSeriesData(lines=lines, step=ctx.suggested_step, url=url)


class PrometheusLabelNamesVariableAttrs(BaseModel):
    datasource: str | None = None
    matchers: list[str] | None = None
    limit: int | None = None


class PrometheusLabelNamesVariableSpec(BaseModel):
    datasource: PrometheusDatasourceSelector
    matchers: list[str] | None = None
    limit: int | None = None


class PrometheusLabelNamesVariablePlugin(ListVariablePlugin[PrometheusLabelNamesVariableSpec], PrometheusPlugin):
    kind = "PrometheusLabelNamesVariable"

    def eval(self, props: dict) -> PrometheusLabelNamesVariableSpec:
        attrs = PrometheusLabelNamesVariableAttrs.model_validate(props)
        return PrometheusLabelNamesVariableSpec(
            datasource=PrometheusDatasourceSelector(name=attrs.datasource),
            matchers=attrs.matchers,
            limit=attrs.limit,
        )

    def fetch(self, spec: PrometheusLabelNamesVariableSpec, ctx: QueryContext) -> ListVariableData:
        datasource = self.get_datasource(spec.datasource, ctx)
        values = datasource.client.label_names(
            start=ctx.start,
            end=ctx.end,
            match=spec.matchers,
            limit=spec.limit,
        )
        return ListVariableData(values=[LabelValue(value=v) for v in values if v != "__name__"])


class PrometheusLabelValuesVariableAttrs(BaseModel):
    datasource: str | None = None
    label_name: str
    matchers: list[str] | None = None
    limit: int | None = None


class PrometheusLabelValuesVariableSpec(BaseModel):
    datasource: PrometheusDatasourceSelector
    label_name: str
    matchers: list[str] | None = None
    limit: int | None = None


class PrometheusLabelValuesVariablePlugin(ListVariablePlugin[PrometheusLabelValuesVariableSpec], PrometheusPlugin):
    kind = "PrometheusLabelValuesVariable"

    def eval(self, props: dict) -> PrometheusLabelValuesVariableSpec:
        attrs = PrometheusLabelValuesVariableAttrs.model_validate(props)
        return PrometheusLabelValuesVariableSpec(
            datasource=PrometheusDatasourceSelector(name=attrs.datasource),
            label_name=attrs.label_name,
            matchers=attrs.matchers,
            limit=attrs.limit,
        )

    def fetch(self, spec: PrometheusLabelValuesVariableSpec, ctx: QueryContext) -> ListVariableData:
        datasource = self.get_datasource(spec.datasource, ctx)
        values = datasource.client.label_values(
            label=spec.label_name,
            start=ctx.start,
            end=ctx.end,
            match=spec.matchers,
            limit=spec.limit,
        )
        return ListVariableData(values=[LabelValue(value=v) for v in values])
