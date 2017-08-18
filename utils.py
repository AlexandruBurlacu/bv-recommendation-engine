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
    values = obj[key]
    [default_dict.update({"genre.{0}.labels.{1}".format(key, val): 1}) for val in values]
    #       ^^^^^^^^^^^^^
    # [WARNING] change in-place

    return default_dict

def make_query(obj):
    """Given a JSON-object with selected filters,
    returns a MongoDB-style query dict"""
    characters_dict = {
        "genre.characters.labels.aliens": {"$in": [0, 1]},
        "genre.characters.labels.mutants": {"$in": [0, 1]},
        "genre.characters.labels.robots": {"$in": [0, 1]},
        "genre.characters.labels.humanoiddroids": {"$in": [0, 1]},
        "genre.characters.labels.dragons": {"$in": [0, 1]},
        "genre.characters.labels.superintelligence": {"$in": [0, 1]}
    }

    space_dict = {
        "genre.spaceSetting.labels.insideearth": {"$in": [0, 1]},
        "genre.spaceSetting.labels.otherplanets": {"$in": [0, 1]},
        "genre.spaceSetting.labels.outerspace": {"$in": [0, 1]},
        "genre.spaceSetting.labels.beyondsolarsystem": {"$in": [0, 1]}

    }

    characters = _preprocess_filter("characters", obj, characters_dict)
    space = _preprocess_filter("spaceSetting", obj, space_dict)
    # time_raw = obj["filters"]["timeSetting"] # TODO: add time settings later
    author = obj["metadata"]["author"]["value"]

    return {
        "$or": [
            {"metadata.author": {"$regex": r"({})\w*".format(author.lower() if author else ""),
                                 "$options": "i"}},
            {**characters}, {**space}
        ]
    }

def key_function(obj):
    """Defines a key for `obj` to make it sortable.

    Parameters
    ----------
    obj : {str: float}
        An element of the returning object of the function `get_candidates`.

    Returns
    -------
    float
        The score of a given object/dict
    """
    return list(obj.values())[0]

def get_sorted(base_title, scores, top_n=5):
    """Sorts the respond body and shapes it before sending over the network"""
    return {base_title: list(sorted(scores[base_title],
                                    key=key_function, reverse=True))[:top_n]}
