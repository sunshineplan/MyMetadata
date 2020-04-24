#!/usr/bin/env python3

from ast import literal_eval
from datetime import datetime
from email.message import EmailMessage
from http.client import HTTPSConnection
from io import BytesIO
from smtplib import SMTP
from subprocess import check_output
from time import sleep

METADATA_SERVER = '$domain'
VERIFY_HEADER = {'$header': '$value'}


def metadata(metadata, default=None, ERROR_IF_NONE=False):
    for _ in range(3):
        try:
            connection = HTTPSConnection(METADATA_SERVER, timeout=10)
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


def backup():
    mongo = metadata('metadata_mongo')
    backup = metadata('metadata_backup')
    if mongo.get('username'):
        command = f"mongodump -h{mongo['server']}:{mongo['port']} -d{mongo['database']} -c{mongo['collection']} -u{mongo['username']} -p{mongo['password']} --gzip --archive"
    else:
        command = f"mongodump -h{mongo['server']}:{mongo['port']} -d{mongo['database']} -c{mongo['collection']} --gzip --archive"
    attachment = BytesIO()
    attachment.write(check_output(command, shell=True))
    msg = EmailMessage()
    msg['Subject'] = f'My Metadata Backup-{datetime.now():%Y%m%d}'
    msg['From'] = backup['sender']
    msg['To'] = backup['subscriber']
    msg.add_attachment(attachment.getvalue(), maintype='application',
                       subtype='octet-stream', filename='database')
    with SMTP(backup['smtp_server'], backup['smtp_server_port']) as s:
        s.starttls()
        s.login(backup['sender'], backup['password'])
        s.send_message(msg)
    print('Backup My Metadata done.')
