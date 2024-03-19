import click


@click.group
def cli() -> None:
    pass


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
