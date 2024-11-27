from datetime import datetime

import pytz

from claspin.model.query import LineData, QueryContext, TimeSeriesData, TimeSeriesQueryPlugin
from claspin.plugins.prometheus.datasource import PrometheusDatasource


class PrometheusPromqlQuery(TimeSeriesQueryPlugin[PrometheusDatasource]):
    query: str

    async def fetch(self, ctx: QueryContext[PrometheusDatasource]) -> TimeSeriesData:
        resp = await ctx.datasource.client.range_query(
            query=self.query,
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
        url = f"{ctx.datasource.url}/query?g0.expr={self.query}"  # TODO: include time range
        return TimeSeriesData(lines=lines, step=ctx.suggested_step, url=url)
