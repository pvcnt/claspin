from typing import Tuple

from claspin.model.datasource import DatasourcePlugin
from claspin.model.query import QueryPlugin
from claspin.plugins.prometheus.plugin import (
    PrometheusDatasource,
    PrometheusLabelNamesQuery,
    PrometheusLabelValuesQuery,
    PrometheusMetricQuery,
    PrometheusPromqlQuery,
)

DATASOURCE_PLUGINS: Tuple[type[DatasourcePlugin], ...] = (PrometheusDatasource,)

QUERY_PLUGINS: Tuple[type[QueryPlugin], ...] = (
    PrometheusLabelNamesQuery,
    PrometheusLabelValuesQuery,
    PrometheusMetricQuery,
    PrometheusPromqlQuery,
)
