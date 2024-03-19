from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

NEGATIVE_INFINITY = float("-inf")
POSITIVE_INFINITY = float("+inf")


class ClaspinModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ObjectMetadata(ClaspinModel):
    name: str
    namespace: Optional[str] = None
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class ClaspinObject(ClaspinModel):
    metadata: ObjectMetadata


class ObjectRef(ClaspinModel):
    name: str
    namespace: Optional[str] = None
