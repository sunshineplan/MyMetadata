#!/usr/bin/env python3

from flask import Flask, request

from metadata._base import Metadata

app = Flask('metadata')


@app.route('/<string:metadata>')
def api(metadata):
    return Metadata(
        app.config['SERVER'],
        app.config['PORT'],
        app.config['DATABASE'],
        app.config['COLLECTION'],
        app.config['USER'],
        app.config['PASSWORD']
    ).get_value(metadata, request)


@app.route('/')
@app.route('/<path:dummy>')
def fallback(dummy=None):
    return '', 403
