#!/usr/bin/env python3

try:
    from ste import encrypt
except:
    from base64 import b64encode

    def encrypt(_, value):
        return b64encode(value.encode())
