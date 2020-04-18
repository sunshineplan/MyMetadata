#!/usr/bin/env python3

import urllib.parse
from datetime import datetime
from email.message import EmailMessage
from http.client import HTTPSConnection
from io import BytesIO
from ipaddress import ip_address, ip_network
from json import loads
from smtplib import SMTP
from subprocess import check_output
from urllib.parse import quote_plus

from flask import Blueprint, request
from pymongo import MongoClient

from .config import *

bp = Blueprint('metadata', __name__)


@bp.route('/<string:metadata>')
def metadata(metadata):
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
    connection = HTTPSConnection(query('encrypt_server')['value'], timeout=10)
    connection.request('POST', '/do', urllib.parse.urlencode(data), headers)
    response = connection.getresponse()
    result = loads(response.read())['result']
    connection.close()
    return result


def backup():
    command = f'mongodump -h{MONGO_SERVER}:{MONGO_PORT} -d{DATABASE} -c{COLLECTION} -u{AUTH} -p{PASSWORD} --gzip --archive'
    attachment = BytesIO()
    attachment.write(check_output(command, shell=True))
    config = query('metadata_backup')
    msg = EmailMessage()
    msg['Subject'] = f'My Metadata Backup-{datetime.now():%Y%m%d}'
    msg['From'] = config['sender']
    msg['To'] = config['subscriber']
    msg.add_attachment(attachment.getvalue(), maintype='application',
                       subtype='octet-stream', filename='database')
    with SMTP(config['smtp_server'], config['smtp_port']) as s:
        s.starttls()
        s.login(config['sender'], config['password'])
        s.send_message(msg)
    print('Backup My Metadata done.')
