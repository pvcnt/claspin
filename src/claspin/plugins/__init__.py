from typing import Tuple

from claspin.plugins.interface import Plugin
from claspin.plugins.panel import (
    GaugeChartPlugin,
    MarkdownPlugin,
    PieChartPlugin,
    StatChartPlugin,
    TablePlugin,
    TimeSeriesChartPlugin,
)
from claspin.plugins.prometheus import (
    PrometheusDatasourcePlugin,
    PrometheusLabelNamesVariablePlugin,
    PrometheusLabelValuesVariablePlugin,
    PrometheusPromqlQueryPlugin,
)
from claspin.plugins.variable import StaticListVariablePlugin

BUILTIN_PLUGINS: Tuple[Plugin, ...] = (
    GaugeChartPlugin(),
    MarkdownPlugin(),
    PieChartPlugin(),
    PrometheusDatasourcePlugin(),
    PrometheusLabelNamesVariablePlugin(),
    PrometheusLabelValuesVariablePlugin(),
    PrometheusPromqlQueryPlugin(),
    StatChartPlugin(),
    StaticListVariablePlugin(),
    TablePlugin(),
    TimeSeriesChartPlugin(),
)
