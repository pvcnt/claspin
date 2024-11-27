from typing import Annotated, Union

from pydantic import Field

from claspin.model.datasource import Datasource
from claspin.model.query import Query
from claspin.model.variable import Variable

Resource = Annotated[
    Union[Datasource, Query, Variable],
    Field(discriminator="kind"),
]
