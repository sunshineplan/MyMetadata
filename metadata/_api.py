#!/usr/bin/env python3

from ast import literal_eval
from http.client import HTTPSConnection
from time import sleep

METADATA_SERVER = ''
VERIFY_HEADER = {'header': 'value'}


def metadata(metadata, default=None, ERROR_IF_NONE=False):
    for _ in range(3):
        try:
            connection = HTTPSConnection(METADATA_SERVER, timeout=5)
            connection.request('GET', f'/{metadata}', headers=VERIFY_HEADER)
            response = connection.getresponse()
            status = response.status
            content = response.read().decode()
            connection.close()
            break
        except:
            status = None
            sleep(5)
    if status == 200:
        try:
            return literal_eval(content)
        except:
            return content
    else:
        if ERROR_IF_NONE:
            raise KeyError
        else:
            return default
