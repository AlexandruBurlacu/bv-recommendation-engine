"""Database utility functions module

This module provides functions for fetching data from database.
"""

# Author: Alexandru Burlacu
# Email:  alexandru-varacuta@bookvoyager.org

import json
import requests


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

def get_book_by(field_name, addr, field_value):
    """Facade function to make the API for fetching the database more uniform
    and to reduce the number of imported functions"""
    if field_name == "id":
        data = _get_book_by_id(addr, field_value)
    elif field_name == "author_or_title":
        data = _search_by_auth_or_title(addr, field_value)
    else:
        raise KeyError("Function get_book_by not defined for field_name '{}', \
available options are {}".format(field_name, ["id", "author_or_title"]))

    return data

def _get_book_by_id(addr, book_id):
    """Get book by MongoDB ID"""
    return db_fetch(addr, {"id": book_id})

def _search_by_auth_or_title(addr, search_token):
    """Given a string, perform a regex search over `author` and `title` fields of a book."""
    token = search_token.lower()
    return db_fetch(addr, {"$or": [{"metadata.author": {"$regex": r"({})\w*".format(token),
                                                        "$options": "i"}},
                                   {"metadata.title":  {"$regex": r"({})\w*".format(token),
                                                        "$options": "i"}}]})
