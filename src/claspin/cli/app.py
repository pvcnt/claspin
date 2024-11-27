from pathlib import Path
from typing import Annotated

import typer
import uvicorn

from claspin.config.parser import ConfigParser
from claspin.format import OutputFormat, dump_resource_stream
from claspin.webapp.app import make_webapp
from claspin.workspace import create_workspace

app = typer.Typer()


@app.command()
def validate(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    workspace = create_workspace(root_dir)
    parser = ConfigParser(workspace)
    parser.load()
    print(f"Successfully loaded {sum(1 for _ in workspace.db.resources)} resources")


@app.command()
def export(
    root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")],
    output_format: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.yaml,
) -> None:
    workspace = create_workspace(root_dir)
    parser = ConfigParser(workspace)
    parser.load()
    print(dump_resource_stream(workspace.db.resources, output_format, indent=2))


@app.command("import")
def import_cmd(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    workspace = create_workspace(root_dir)
    parser = ConfigParser(workspace)
    parser.load()


@app.command()
def lint(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    workspace = create_workspace(root_dir)
    parser = ConfigParser(workspace)
    for lint in parser.lint():
        print(f"[{lint.severity}] {lint}")


@app.command()
def serve(
    root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")],
    host: str = "127.0.0.1",
    port: int = 8080,
) -> None:
    workspace = create_workspace(root_dir)
    parser = ConfigParser(workspace)
    parser.load()
    webapp = make_webapp(workspace)
    uvicorn.run(webapp, host=host, port=port)
