from typing import Annotated, Union

from pydantic import Field

from claspin.model.datasource import Datasource
from claspin.model.query import Query

Resource = Annotated[
    Union[Datasource, Query],
    Field(discriminator="kind"),
]
