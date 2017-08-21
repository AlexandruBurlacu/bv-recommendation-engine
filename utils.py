"""Utility functions module

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
    kv_pairs = obj[key].items()
    [default_dict.update({"genre.{0}.labels.{1}".format(key, k): v}) for k, v in kv_pairs if v == 1]
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

def get_full_objs_decorator(func):
    """Adds the full object about given title. Fetches it from DB."""
    addr = get_config()["mongo_rest_interface_addr"]
    get_obj = lambda t: json.loads(preprocess_resp(search_by_auth_or_title(addr, t)))[0]
    get_overall_sentiment = lambda o: o["sentiment"]["overall"][0]

    def __inner(base_title, scores, *args, **kwargs):
        resp = func(base_title, scores, *args, **kwargs)
        head_obj, *tail_objs = resp["resp"]

        base_obj = get_obj(head_obj["title"])

        for kvs in tail_objs:
            kvs["title"] = get_obj(kvs["title"])

            kvs["title"]["sentiment"]["overall"] = {"current": get_overall_sentiment(kvs["title"]),
                                                    "base": get_overall_sentiment(base_obj)}
        _, *top_matches = resp["resp"]
        return {"resp": top_matches}
    return __inner

@get_full_objs_decorator
def get_sorted(base_title, scores, top_n=5):
    """Sorts the respond body and shapes it before sending over the network"""
    return {"resp": list(sorted(scores[base_title],
                                key=lambda x: x["score"], reverse=True))[:top_n + 1]}


def _reshape_timeline(checkpoints):
    return map(lambda x: x, checkpoints)

def preprocess_resp(raw_resp):
    """Transforma the sentiment timeline dict of the response body.

    It's ugly as hell, sorry.

    Parameters
    ----------
    raw_resp : dict of {"resp": [dict]}
        The response dictionary fetched, and optionaly preprocessed, from database.

    Returns
    -------
    resp : list
        List with dictionaries with modified structure of the value under
        the `timeline` key of the `sentiment` dictionary
    dict
        {"Content-Type": "application/json"}

    Example
    -------
    >>> obj =  \"""{"resp":
    ...    [{"sentiment":
    ...       {"timeline":
    ...            [
    ...                [1, "joy", "hope", 1936],
    ...                [1, "joy", "hope", 3597]
    ...           ]}
    ...    }]}\"""
    >>> preprocess_resp(obj)
    '[{"sentiment": {"timeline": [[1, "joy", "hope", 1936], [1, "joy", "hope", 3597]]}}]'
    """
    resp = json.loads(raw_resp)["resp"]
    condition = len(resp)
    if condition == 1:
        timeline = _reshape_timeline(resp[0]["sentiment"]["timeline"])
        resp[0]["sentiment"].update({"timeline": list(timeline)}) # [WARNING] change in-place
    elif condition > 1:
        timelines = [_reshape_timeline(r["sentiment"]["timeline"]) for r in resp]
        [r["sentiment"].update({"timeline": list(timeline)}) # [WARNING] change in-place
         for r, timeline in zip(resp, timelines)]
    return json.dumps(resp)
