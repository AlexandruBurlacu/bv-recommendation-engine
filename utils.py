"""utils module

This module provides utility functions.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

import json
import os
import requests

PATH = os.path.abspath(os.path.dirname(__file__))

def compose(f_fun, g_fun):
    """Composition of unary functions"""
    return lambda x: f_fun(g_fun(x))

def get_config(config_file_path=os.path.join(PATH, "config.json")):
    """Loads the configuration file.

    Parameters
    ----------
    config_file_path : str, optional
        The path to the configuration file.

    Returns
    -------
    dict
        The configuration dict object.
    """
    with open(config_file_path) as config_ptr:
        return json.load(config_ptr)

def db_fetch(db_service_url, constraints):
    """Wraps the underling request to the database service.

    Parameters
    ----------
    db_service_url : str
    constraints : dict
        The PyMongo-style query object.

    Returns
    -------
    dict
        The result of the applied query.
    """
    resp = requests.post(db_service_url + "/fetch",
                         json={"constraints": json.dumps(constraints)},
                         headers={"content-type": "application/json"})
    return json.loads(resp.content.decode("utf-8"))

def get_book_by_id(book_id):
    """Get book by MongoDB ID"""
    return db_fetch(get_config()["mongo_rest_interface_addr"], {"id": book_id})

def search_by_auth_or_title(search_token):
    return db_fetch(get_config()["mongo_rest_interface_addr"],
                    {"$or": [{"metadata.author": search_token},
                             {"metadata.title": search_token}]})

