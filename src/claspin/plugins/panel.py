from enum import StrEnum, unique
from typing import Annotated, Optional

from pydantic import Field

from claspin.model.common import BaseModel, Calculation, Unit
from claspin.plugins.interface import PanelPlugin


@unique
class Sort(StrEnum):
    ASC = "asc"
    DESC = "desc"


@unique
class ChartMode(StrEnum):
    VALUE = "value"
    PERCENTAGE = "percentage"


@unique
class LegendMode(StrEnum):
    LIST = "list"
    TABLE = "table"


@unique
class LegendPosition(StrEnum):
    BOTTOM = "bottom"
    RIGHT = "right"


@unique
class LegendSize(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"


class Legend(BaseModel):
    position: LegendPosition = LegendPosition.BOTTOM
    mode: LegendMode = LegendMode.LIST
    size: LegendSize = LegendSize.MEDIUM
    values: list[Calculation] = Field(default_factory=list)


@unique
class ColorMode(StrEnum):
    FIXED = "fixed"
    FIXED_SINGLE = "fixed-single"


class QuerySettings(BaseModel):
    query_index: int
    color_mode: ColorMode
    color_value: str = Field(pattern="^#(?:[0-9a-fA-F]{3}){1,2}$")


@unique
class PaletteMode(StrEnum):
    AUTO = "auto"
    CATEGORICAL = "categorical"


@unique
class VisualShowPoints(StrEnum):
    AUTO = "auto"
    ALWAYS = "always"


@unique
class VisualStack(StrEnum):
    ALL = "all"
    PERCENT = "percent"


@unique
class VisualDisplay(StrEnum):
    LINE = "line"
    BAR = "bar"


class Palette(BaseModel):
    mode: PaletteMode = PaletteMode.AUTO


class Visual(BaseModel):
    display: VisualDisplay = VisualDisplay.LINE
    line_width: Optional[Annotated[float, Field(ge=0.25, le=3)]] = None
    area_opacity: Optional[Annotated[float, Field(ge=0, le=1)]] = None
    show_points: VisualShowPoints = VisualShowPoints.AUTO
    palette: Palette = Field(default_factory=Palette)
    point_radius: Optional[Annotated[float, Field(ge=0, le=6)]] = None
    stack: Optional[VisualStack] = None
    connect_nulls: bool = False


class Sparkline(BaseModel):
    color: Optional[str] = None
    width: Optional[int] = None


class Format(BaseModel):
    unit: Unit | None = None
    decimal_places: Optional[int] = None
    short_values: bool = False


@unique
class ThresholdMode(StrEnum):
    PERCENT = "percent"
    ABSOLUTE = "absolute"


class ThresholdStep(BaseModel):
    value: float
    color: Optional[str] = None
    name: Optional[str] = None


class Thresholds(BaseModel):
    mode: Optional[ThresholdMode] = None
    default_color: Optional[str] = None
    steps: list[ThresholdStep] = Field(default_factory=list)


class BarChartSpec(BaseModel):
    calculation: Calculation
    format: Format = Field(default_factory=Format)
    sort: Sort = Sort.ASC
    mode: ChartMode = ChartMode.VALUE


class BarChartPlugin(PanelPlugin[BarChartSpec]):
    kind = "BarChart"

    def eval(self, props: dict) -> BarChartSpec:
        return BarChartSpec.model_validate({})


class GaugeChartSpec(BaseModel):
    calculation: Calculation
    format: Optional[Format] = None
    thresholds: Optional[Thresholds] = None
    max: Optional[float] = None


class GaugeChartPlugin(PanelPlugin[GaugeChartSpec]):
    kind = "GaugeChart"

    def eval(self, props: dict) -> GaugeChartSpec:
        return GaugeChartSpec.model_validate({})


class MarkdownSpec(BaseModel):
    text: str


class MarkdownPlugin(PanelPlugin[MarkdownSpec]):
    kind = "Markdown"

    def eval(self, props: dict) -> MarkdownSpec:
        return MarkdownSpec.model_validate({})


class PieChartSpec(BaseModel):
    calculation: Calculation
    radius: int
    format: Format = Field(default_factory=Format)
    sort: Optional[Sort] = None
    mode: Optional[ChartMode] = None
    legend: Optional[Legend] = None
    query_settings: list[QuerySettings] = Field(default_factory=list)
    visual: Visual = Field(default_factory=Visual)


class PieChartPlugin(PanelPlugin[PieChartSpec]):
    kind = "PieChart"

    def eval(self, props: dict) -> PieChartSpec:
        return PieChartSpec.model_validate({})


class StatChartAttrs(BaseModel):
    calculation: Calculation
    unit: Unit | None = None
    decimal_places: Optional[int] = None
    short_values: bool = False
    sparkline: bool = False
    sparkline_color: Optional[str] = None
    sparkline_width: Optional[int] = None
    value_font_size: Optional[int] = None


class StatChartSpec(BaseModel):
    calculation: Calculation
    format: Format = Field(default_factory=Format)
    thresholds: Optional[Thresholds] = None
    sparkline: Optional[Sparkline] = None
    value_font_size: Optional[int] = None


class StatChartPlugin(PanelPlugin[StatChartSpec]):
    kind = "StatChart"

    def eval(self, props: dict) -> StatChartSpec:
        attrs = StatChartAttrs.model_validate(props)
        return StatChartSpec(
            calculation=attrs.calculation,
            format=Format(
                unit=attrs.unit,
                decimal_places=attrs.decimal_places,
                short_values=attrs.short_values,
            ),
            sparkline=Sparkline(
                color=attrs.sparkline_color,
                width=attrs.sparkline_width,
            )
            if attrs.sparkline
            else None,
            value_font_size=attrs.value_font_size,
        )


@unique
class TableDensity(StrEnum):
    COMPACT = "compact"
    STANDARD = "standard"
    COMFORTABLE = "comfortable"


@unique
class TableAlign(StrEnum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TableColumnSettings(BaseModel):
    name: str = Field(min_length=1)
    header: Optional[str] = None
    header_description: Optional[str] = None
    cell_description: Optional[str] = None
    align: TableAlign = TableAlign.LEFT
    enable_sorting: bool = False
    width: Optional[int] = None
    hide: bool = False


class TableSpec(BaseModel):
    density: TableDensity = TableDensity.STANDARD
    column_settings: list[TableColumnSettings] = Field(default_factory=list)


class TablePlugin(PanelPlugin[TableSpec]):
    kind = "Table"

    def eval(self, props: dict) -> TableSpec:
        return TableSpec.model_validate({})


class Tooltip(BaseModel):
    enable_pinning: bool = True


class YAxis(BaseModel):
    show: bool = True
    label: Optional[str] = None
    format: Optional[Format] = None
    min: Optional[float] = None
    max: Optional[float] = None


class TimeSeriesChartSpec(BaseModel):
    legend: Optional[Legend] = None
    tooltip: Tooltip = Field(default_factory=Tooltip)
    y_axis: YAxis = Field(default_factory=YAxis)
    thresholds: Optional[Thresholds] = None
    visual: Visual = Field(default_factory=Visual)
    query_settings: list[QuerySettings] = Field(default_factory=list)


class TimeSeriesChartPlugin(PanelPlugin[TimeSeriesChartSpec]):
    kind = "TimeSeriesChart"

    def eval(self, props: dict) -> TimeSeriesChartSpec:
        return TimeSeriesChartSpec.model_validate({})
