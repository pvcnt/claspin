from typing import Tuple, Type

from claspin.model.common import Plugin
from claspin.plugins.prometheus.datasource import PrometheusDatasource
from claspin.plugins.prometheus.query import PrometheusPromqlQuery
from claspin.plugins.prometheus.variable import (
    PrometheusLabelNamesVariable,
    PrometheusLabelValuesVariable,
)

BUILTIN_PLUGINS: Tuple[Type[Plugin], ...] = (
    PrometheusDatasource,
    PrometheusLabelNamesVariable,
    PrometheusLabelValuesVariable,
    PrometheusPromqlQuery,
)
