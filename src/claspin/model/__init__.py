from typing import Annotated, Union

from pydantic import Field

from claspin.model.dashboard import Dashboard, EphemeralDashboard
from claspin.model.datasource import Datasource
from claspin.model.panel import Panel
from claspin.model.project import Project
from claspin.model.query import Query
from claspin.model.variable import Variable

Resource = Annotated[
    Union[Project, Datasource, Query, Variable, Panel, Dashboard, EphemeralDashboard],
    Field(discriminator="kind"),
]
