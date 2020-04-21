#!/usr/bin/env python3

from metadata.server import app

app.config.from_pyfile('config.py', silent=True)

if __name__ == '__main__':
    app.run()
