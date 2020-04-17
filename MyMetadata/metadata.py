#!/usr/bin/env python3

import urllib.parse
from http.client import HTTPSConnection
from ipaddress import ip_address, ip_network
from json import loads
from urllib.parse import quote_plus

from flask import Blueprint, request
from pymongo import MongoClient

from .config import *

bp = Blueprint('metadata', __name__)


@bp.route('/<string:metadata>')
def api(metadata):
    remote_addr = ip_address(request.remote_addr)
    verify = query('metadata_verify')
    header = request.headers.get(verify['header'])
    if not header or header != verify['content']:
        return '', 403
    metadata = query(metadata)
    if not metadata or not metadata.get('value'):
        return '', 404
    whitelist = metadata.get('whitelist')
    if whitelist:
        allow = 0
        if remote_addr == ip_address('127.0.0.1'):
            allow = 1
        else:
            try:
                for IP_or_CIDR in whitelist:
                    if remote_addr in ip_network(IP_or_CIDR):
                        allow = 1
                        break
            except:
                return '', 500
        if not allow:
            return '', 403
    if metadata.get('encrypt'):
        return encrypt(query('key')['value'], str(metadata['value']))
    else:
        return str(metadata['value'])


@bp.route('/')
@bp.route('/<path:dummy>')
def fallback(dummy=None):
    return '', 400


def query(metadata):
    if AUTH:
        username = quote_plus(AUTH)
        password = quote_plus(PASSWORD)
        URI = f'mongodb://{username}:{password}@{MONGO_SERVER}:{MONGO_PORT}/{DATABASE}'
    else:
        URI = f'mongodb://{MONGO_SERVER}:{MONGO_PORT}'
    with MongoClient(URI) as client:
        metadata = client[DATABASE][COLLECTION].find_one({'_id': metadata})
    return metadata


def encrypt(key, plaintext):
    data = {'mode': 'encrypt', 'key': key, 'content': plaintext}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    connection = HTTPSConnection(query('encrypt_server'), timeout=10)
    connection.request('POST', '/do', urllib.parse.urlencode(data), headers)
    response = connection.getresponse()
    result = loads(response.read())['result']
    connection.close()
    return result
