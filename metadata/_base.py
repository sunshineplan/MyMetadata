#!/usr/bin/env python3

from base64 import b64encode
from ipaddress import ip_address, ip_network
from json import dumps

from urllib.parse import quote_plus

from pymongo import MongoClient

try:
    from ste import encrypt
except:
    def encrypt(_, value):
        return b64encode(value.encode())


class Metadata:
    def __init__(self, mongo_server, mongo_port=27017, database='metadata', collection='metadata', user=None, pwd=None):
        self.server = mongo_server
        self.port = mongo_port
        self.db = database
        self.col = collection
        self.user = user
        self.pwd = pwd

    def query(self, metadata):
        if self.user:
            username = quote_plus(self.user)
            password = quote_plus(self.pwd)
            URI = f'mongodb://{username}:{password}@{self.server}:{self.port}/{self.db}'
        else:
            URI = f'mongodb://{self.server}:{self.port}'
        with MongoClient(URI) as client:
            metadata = client[self.db][self.col].find_one({'_id': metadata})
        return metadata

    def get_value(self, metadata, request):
        remote_addr = ip_address(request.remote_addr)
        verify = self.query('metadata_verify')
        header = request.headers.get(verify['header'])
        if not header or header != verify['content']:
            return '', 403
        metadata = self.query(metadata)
        if not metadata or not metadata.get('value'):
            return '', 404
        whitelist = metadata.get('whitelist')
        if whitelist is not None:
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
        value = dumps(metadata['value'])
        if metadata.get('encrypt'):
            try:
                key = b64encode(self.query('key')['value'].encode()).decode()
                return encrypt(key, value)
            except:
                return b64encode(value.encode())
        else:
            return value
