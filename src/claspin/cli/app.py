from pathlib import Path
from typing import Annotated

import typer
import uvicorn

from claspin.format import OutputFormat, dump_resource_stream
from claspin.runtime import Runtime
from claspin.webapp.app import make_webapp

app = typer.Typer()


@app.command()
def validate(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    runtime = Runtime(root_dir)
    runtime.parser.eval()
    print(f"Successfully loaded {sum(1 for _ in runtime.db.entities)} resources")


@app.command()
def export(
    root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")],
    output_format: Annotated[OutputFormat, typer.Option("--output", "-o")] = OutputFormat.YAML,
) -> None:
    runtime = Runtime(root_dir)
    runtime.parser.eval()
    print(dump_resource_stream(runtime.db.entities, output_format, indent=2))


@app.command("migrate")
def migrate(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    pass


@app.command()
def lint(root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")]) -> None:
    runtime = Runtime(root_dir)
    for lint in runtime.parser.lint():
        print(f"[{lint.severity}] {lint}")


@app.command()
def serve(
    root_dir: Annotated[Path, typer.Option(..., "--workspace", "-w")],
    host: str = "127.0.0.1",
    port: int = 8080,
) -> None:
    runtime = Runtime(root_dir)
    runtime.parser.eval()
    webapp = make_webapp(runtime)
    uvicorn.run(webapp, host=host, port=port)
