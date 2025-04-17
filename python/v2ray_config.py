#!/usr/bin/env python3

import requests
from base64 import b64decode
from urllib.parse import unquote, urlsplit
import collections
import re
import sys, os
import json

def pad_base64(encoded):
    r = len(encoded) % 4
    if r > 0:
        encoded += '=' * r
    return encoded

def decode_base64(encoded):
    encoded = pad_base64(encoded)
    return b64decode(encoded)

V2RAY_CONFIG_DIR = "/usr/local/etc/v2ray"

V2RAY_SUBCRIPTION_FILE = os.path.join(V2RAY_CONFIG_DIR, 'subscription.txt')
subscription = None
if os.path.exists(V2RAY_SUBCRIPTION_FILE):
    with open(V2RAY_SUBCRIPTION_FILE, 'r') as f:
        subscription = f.read().strip()
        if len(subscription) == 0:
            subscription = None

flag_debug = False
flag_dryrun = False
for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    larg = arg.lower()
    if larg in ['--dryrun']:
        flag_dryrun = True
    elif larg in ['--debug']:
        flag_debug = True
    else:
        subscription = arg

if subscription is None:
    print("ERROR: no subscription provided")
    exit(1)

headers = {
        'User-Agent': 'v2rayN/7.11.1'
    }

original_links = decode_base64(requests.get(subscription, headers=headers).text).decode('utf-8').splitlines()
links = [urlsplit(link) for link in original_links]

SSEndpoint = collections.namedtuple(
        'SSEndpoint',
        ['address', 'method', 'password', 'port', 'banner']
    )

def parse_link(link):
    banner = link.fragment
    netloc = decode_base64(link.netloc).decode('utf-8').split(':')
    method = netloc[0]
    password, address = tuple(netloc[1].split('@'))
    port  = int(netloc[2])
    return SSEndpoint(address=address, method=method, password=password, port=port, banner=banner)

endpoints = [parse_link(link) for link in links]

V2RAY_CONFIG_FILE = os.path.join(V2RAY_CONFIG_DIR, 'config.json')

with open(V2RAY_CONFIG_FILE, 'r') as f:
    config_content = json.load(f)

if not 'outbounds' in config_content:
    config_content['outbounds'] = []
try:
    outbound = next(filter(lambda outbound: outbound['protocol'] == 'shadowsocks', config_content['outbounds']))
except:
    outbound = {
            'protocol': 'shadowsocks',
            'settings': {
                'servers': []
            }
    }
    config_content['outbounds'].append(outbound)
outbound['settings']['servers'] = [{
                    'address': endpoint.address,
                    'method': endpoint.method,
                    'ota': False,
                    'password': endpoint.password,
                    'port': endpoint.port
                } for endpoint in endpoints]

if flag_dryrun:
    pass
else:
    with open(V2RAY_CONFIG_FILE, 'w') as f:
        json.dump(config_content, f, indent=4)

if flag_debug:
    import code
    code.interact("", local=locals())

