#!/usr/bin/env python
# Kyle Fitzsimmons, 2015
from bunch import bunchify
import os
import yaml

def load(conf_file=None):
    if not conf_file:
        conf_file = 'settings.yaml'
    if os.path.exists(conf_file):
        with open(conf_file, 'r') as conf_f:
            # load yaml settings to an object
            conf = bunchify(yaml.load(conf_f))
        return conf
    else:
        default = {
            'email': {
                'address': 'loopback@test.com',
                'server': 'smtp.isp.com',
                'port': 465, # must be SSL,
                'username': 'sndr@test.com',
                'password': 'hunter2',
            },
            'modules': {
                'transitfeeds_api': 'abcd1234'
            }
        }
        with open(conf_file, 'w') as conf_f:
            conf_f.write(yaml.dump(default, default_flow_style=False))
        return

def save_schema(columns):
    # for saving database configuration to a file
    schema_file = 'settings_db.yaml'
    with open(schema_file, 'w') as schema_f:
        schema_f.write(yaml.dump(columns, default_flow_style=False))
