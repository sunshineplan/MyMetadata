#!/usr/bin/env python3

from flask import Flask

from MyMetadata import metadata

app = Flask(__name__)
app.register_blueprint(metadata.bp)
