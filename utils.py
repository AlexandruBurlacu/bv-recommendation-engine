"""utils module

This module provides utility functions.
"""

# Author: Alexandru Varacuta
# Email:  alexandru-varacuta@bookvoyager.org

import json
import os
import requests

PATH = os.path.abspath(os.path.dirname(__file__))

def drop_none(word_iter):
    return filter(lambda x: x[:2] != (None, None), word_iter)

def get_config(config_file_path = os.path.join(PATH, "config.json")):
    with open(config_file_path) as config_ptr:
        return json.load(config_ptr)

def db_fetch(db_service_url, constraints):
    """Wraps the underling request to the database service."""
    resp = requests.post(db_service_url + "/fetch",
                         json={"constraints": json.dumps(constraints)},
                         headers={"content-type": "application/json"})
    return json.loads((resp.content).decode("utf-8"))

