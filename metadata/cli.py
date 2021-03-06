#!/usr/bin/env python3

import click

from metadata._api import backup as _backup
from metadata._base import Metadata
from metadata.server import app

options = [
    click.option('--server', '-s', default='localhost', help='Mongo Server'),
    click.option('--port', '-P', default=27017, help='Mongo Server Port'),
    click.option('--database', '-d', default='metadata', help='Database'),
    click.option('--collection', '-c', default='metadata', help='Collection'),
    click.option('--user', '-u', default='metadata', help='Mongodb User'),
    click.option('--pwd', '-p', help='Mongodb User Password')
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


@click.group()
def cli():
    pass


@cli.command(short_help='Query metadata')
@click.argument('metadata')
@add_options(options)
def query(server, port, database, collection, user, pwd, metadata):
    click.echo(Metadata(server, port, database,
                        collection, user, pwd).query(metadata))


@cli.command(short_help='Backup Database')
def backup():
    try:
        _backup()
    except:
        click.echo('Failed. Please check mail setting.')


@cli.command(short_help='Run Server')
@add_options(options)
@click.option('--host', '-h', default='localhost', help='Listening Host')
@click.option('--listen-port', default=80, help='Listening Port')
@click.option('--debug', is_flag=True)
def run(server, port, database, collection, user, pwd, host, listen_port, debug):
    app.config['SERVER'] = server
    app.config['PORT'] = port
    app.config['DATABASE'] = database
    app.config['COLLECTION'] = collection
    app.config['USER'] = user
    app.config['PASSWORD'] = pwd
    app.run(host=host, port=listen_port, debug=debug)


def main():
    cli()


if __name__ == '__main__':
    main()
