"""Utility functions module

This module provides utility functions.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

import json
import os

from .db_utils import get_book_by

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

def _preprocess_filter(key, obj, default_dict):
    """If filter object, at the given `key` has value 1,
    it modifies the `default_dict` else it leaves it untouched.
    The only inconvenience is that the change is in place.
    """
    [default_dict.update({"genre.{0}.labels.{1}".format(key, k): v}) # [WARNING] change in-place
     for k, v in obj[key].items() if v == 1]

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
            {"metadata.author": {"$regex": r"({})\w*".format(author if author else ""),
                                 "$options": "i"}},
            {**characters}, {**space}
        ]
    }

def _get_full_objs_decorator(func):
    """Adds the full object about given title. Fetches it from DB.
    Also, the decorator enriches the `sentiment.overall` field of the top matching titles
    with the base title's `sentiment.overall` list of objects.

    From [{"score": float, "title": str}]
    To   [{"score": float, "title": obj] where obj is similart
    to the response from "/api/v1/books/<book_id>" endpoit but with the `sentiment.overall` field
    now containing 2 items, on index 0 the base book's object and on index 1 the current's one.
    """
    addr = get_config()["mongo_rest_interface_addr"]
    get_obj = lambda t: json.loads(preprocess_resp(get_book_by("author_or_title", addr, t)))[0]
    get_overall_sentiment = lambda o: o["sentiment"]["overall"][0]

    def __inner(base_title, scores, *args, **kwargs):
        resp = func(base_title, scores, *args, **kwargs)
        head_obj, *tail_objs = resp["resp"]

        base_obj = get_obj(head_obj["title"])

        for kvs in tail_objs:
            kvs["title"] = get_obj(kvs["title"])

            kvs["title"]["sentiment"]["overall"] = [get_overall_sentiment(base_obj),
                                                    get_overall_sentiment(kvs["title"])]
        _, *top_matches = resp["resp"]
        return top_matches
    return __inner

@_get_full_objs_decorator
def get_sorted(base_title, scores, top_n=5):
    """Sorts the respond body and reshapes it before sending over the network"""
    return {"resp": list(sorted(scores[base_title],
                                key=lambda x: x["score"], reverse=True))[:top_n + 1]}

def preprocess_resp(raw_resp):
    """Transform the sentiment timeline dict of the response body.

    Parameters
    ----------
    raw_resp : dict of {"resp": [dict]}
        The response dictionary fetched, and optionaly preprocessed, from database.

    Returns
    -------
    resp : list
        List with dictionaries with modified structure of the value under
        the `timeline` key of the `sentiment` dictionary
    """
    resp = json.loads(raw_resp)["resp"]

    timelines = (r["sentiment"]["timeline"] for r in resp)
    [r["sentiment"].update({"timeline": list(timeline)}) # [WARNING] change in-place
     for r, timeline in zip(resp, timelines)]

    return json.dumps(resp)
