from typing import Tuple, Type

from claspin.model.common import Plugin
from claspin.plugins.prometheus.datasource import PrometheusDatasource
from claspin.plugins.prometheus.query import (
    PrometheusLabelNamesVariable,
    PrometheusLabelValuesVariable,
    PrometheusPromqlQuery,
)

BUILTIN_PLUGINS: Tuple[Type[Plugin], ...] = (
    PrometheusDatasource,
    PrometheusLabelNamesVariable,
    PrometheusLabelValuesVariable,
    PrometheusPromqlQuery,
)
