from typing import Literal, Optional

from pydantic import Field

from claspin.model.common import BaseModel, Display, Entity, JSONRef
from claspin.model.panel import Panel
from claspin.model.variable import VariableSpec


class GridLayoutCollapse(BaseModel):
    open: bool


class GridLayoutDisplay(BaseModel):
    title: Optional[str] = None
    collapse: Optional[GridLayoutCollapse] = None


class GridItem(BaseModel):
    x: int
    y: int
    width: int
    height: int
    content: JSONRef


class GridLayoutSpec(BaseModel):
    display: GridLayoutDisplay = Field(default_factory=GridLayoutDisplay)
    items: list[GridItem] = Field(default_factory=list)


class GridLayout(BaseModel):
    kind: Literal["Grid"] = "Grid"
    spec: GridLayoutSpec


class DashboardSpec(BaseModel):
    display: Display = Field(default_factory=Display)
    variables: list[VariableSpec] = Field(default_factory=list)
    panels: dict[str, Panel] = Field(default_factory=dict)
    layouts: list[GridLayout] = Field(default_factory=list)
    duration: Optional[str] = None
    refresh_interval: Optional[str] = None


class Dashboard(Entity):
    spec: DashboardSpec


class EphemeralDashboardSpec(DashboardSpec):
    ttl: str


class EphemeralDashboard(Entity):
    spec: EphemeralDashboardSpec
