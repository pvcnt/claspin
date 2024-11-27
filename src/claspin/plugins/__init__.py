from typing import Tuple

from claspin.plugins.interface import Extension
from claspin.plugins.prometheus.extension import PrometheusExtension

BUILTIN_EXTENSIONS: Tuple[Extension] = (PrometheusExtension(),)
