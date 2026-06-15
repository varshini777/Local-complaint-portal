import click
from flask.cli import with_appcontext

from backend.services.seed_service import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_OFFICER_EMAIL,
    seed_development_data,
)


@click.command("seed-data")
@with_appcontext
def seed_data_command():
    result = seed_development_data()

    if not result.get("success"):
        click.echo("Seed failed.")
        click.echo(f"Error: {result.get('error')}")
        raise click.ClickException("Seed data could not be created.")

    click.echo("Seed completed.")
    click.echo()
    click.echo(f"Admin: {DEFAULT_ADMIN_EMAIL}")
    click.echo(f"Officer: {DEFAULT_OFFICER_EMAIL}")
    click.echo("Ward: W001")
    click.echo(f"Categories Added: {result.get('categories_created', 0)}")
    click.echo(f"Settings Added: {result.get('settings_created', 0)}")


def register_cli_commands(app):
    app.cli.add_command(seed_data_command)
