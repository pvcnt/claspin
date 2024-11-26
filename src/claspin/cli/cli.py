from pathlib import Path

import click

from claspin.server import start_server
from claspin.workspace import create_workspace


@click.group
def cli() -> None:
    pass


@cli.command
def validate() -> None:
    pass


@click.option(
    "--workspace",
    "-w",
    "root_dir",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@cli.command
def export(root_dir: Path) -> None:
    workspace = create_workspace(root_dir)
    workspace.parse()
    click.echo("\n---\n".join(ent.model_dump_yaml() for ent in workspace.resources))


@click.option(
    "--workspace",
    "-w",
    "root_dir",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@cli.command
def lint(root_dir: Path) -> None:
    workspace = create_workspace(root_dir)
    for lint in workspace.lint():
        click.echo(f"[{lint.severity}] {lint}")


@click.option(
    "--workspace",
    "-w",
    "root_dir",
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--host", "-h", default="127.0.0.1")
@click.option("--port", "-p", default=8080)
@cli.command
def serve(root_dir: Path, host: str, port: int) -> None:
    workspace = create_workspace(root_dir)
    workspace.parse()
    start_server(host=host, port=port, workspace=workspace)
