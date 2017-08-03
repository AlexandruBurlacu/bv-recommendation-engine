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

def get_book_by_id(addr, book_id):
    """Get book by MongoDB ID"""
    return db_fetch(addr, {"id": book_id})

def search_by_auth_or_title(addr, search_token):
    """Given a string, perform a regex search over `author` and `title` fields of a book."""
    token = search_token.lower()
    return db_fetch(addr, {"$or": [{"metadata.author": {"$regex": r"({})\w*".format(token),
                                                        "$options": "i"}},
                                   {"metadata.title":  {"$regex": r"({})\w*".format(token),
                                                        "$options": "i"}}]})

def _preprocess_filter(key, obj, default_dict):
    values = map(lambda v: v.lower().replace("_", ""), obj["filters"][key])
    [default_dict.update({val: 1}) for val in values] # [WARNING] change in-place

    return default_dict



def make_query(obj):
    """Given a JSON-object with selected filters,
    returns a MongoDB-style query dict"""
    characters_dict = {
        "aliens": 0,
        "mutants": 0,
        "robots": 0,
        "humanoiddroids": 0,
        "dragons": 0,
        "superintelligence": 0
    }

    space_dict = {
        "insideearth": 0,
        "otherplanets": 0,
        "outerspace": 0,
        "beyondsolarsystem": 0

    }

    characters = _preprocess_filter("characters", obj, characters_dict)
    space = _preprocess_filter("spaceSetting", obj, space_dict)
    # time_raw = obj["filters"]["timeSetting"] # TODO: add time settings later

    author = obj["filters"]["metadata"]["author"]["value"].lower()

    return {
        "metadata.author": author,
        "genre.characters.labels": characters,
        "genre.space.labels": space
        }
