from enum import StrEnum, unique
from typing import Iterable

from claspin.model.common import Entity


@unique
class OutputFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"


def dump_resource(resource: Entity, format: OutputFormat, indent: int | None = None) -> str:
    if format == OutputFormat.JSON:
        return resource.model_dump_json(exclude_unset=True, indent=indent)
    elif format == OutputFormat.YAML:
        return resource.model_dump_yaml(exclude_unset=True, indent=indent)


def dump_resource_stream(resources: Iterable[Entity], format: OutputFormat, indent: int | None = None) -> str:
    if format == OutputFormat.JSON:
        return "[" + ", ".join(dump_resource(res, format, indent) for res in resources) + "]"
    elif format == OutputFormat.YAML:
        return "\n---\n".join(dump_resource(res, format, indent) for res in resources)
