#!/usr/bin/env python3

from http.client import HTTPSConnection
from json import loads
from urllib.parse import urlencode

SERVER = ''


def encrypt(key, plaintext):
    data = {'mode': 'encrypt', 'key': key, 'content': plaintext}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    connection = HTTPSConnection(SERVER, timeout=10)
    connection.request('POST', '/do', urlencode(data), headers)
    response = connection.getresponse()
    result = loads(response.read())['result']
    connection.close()
    return result
