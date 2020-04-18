#!/usr/bin/env python3

import click

from MyMetadata import app
from MyMetadata.metadata import backup as _backup


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(run)


@cli.command(short_help='Backup Database')
def backup():
    try:
        _backup()
    except:
        click.echo('Failed. Please check mail setting.')


@cli.command(short_help='Run Server')
@click.option('--port', '-p', default=80, help='Listening Port')
@click.option('--debug', is_flag=True, hidden=True)
def run(port, debug):
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    cli()
