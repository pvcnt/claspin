from enum import StrEnum, unique
from typing import Iterable

from claspin.model import Resource


@unique
class OutputFormat(StrEnum):
    json = "Json"
    yaml = "Yaml"


def dump_resource(resource: Resource, format: OutputFormat, indent: int | None = None) -> str:
    if format == OutputFormat.json:
        return resource.model_dump_json(exclude_unset=True, indent=indent)
    elif format == OutputFormat.yaml:
        return resource.model_dump_yaml(exclude_unset=True, indent=indent)
    else:
        raise AssertionError()


def dump_resource_stream(resources: Iterable[Resource], format: OutputFormat, indent: int | None = None) -> str:
    if format == OutputFormat.json:
        return "[" + ", ".join(dump_resource(res, format, indent) for res in resources) + "]"
    elif format == OutputFormat.yaml:
        return "\n---\n".join(dump_resource(res, format, indent) for res in resources)
    else:
        raise AssertionError()
