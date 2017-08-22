"""API module

Here are defined all endpoints of the Recommendation Service API, namely
GET `/api/v1/books/<book_id>` to get information about a book queried by ID
GET `/api/v1/books?q` to get books by title or author's name
POST `/api/v1/books/<book_id>/recommendations` to get book recommendations for a book by ID
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request

from logic import get_candidates
from utils import get_config, get_sorted, make_query, preprocess_resp
from db_utils import get_book_by, db_fetch

app = Flask(__name__)

DB_ADDRESS = get_config()["mongo_rest_interface_addr"]

handler = RotatingFileHandler(get_config()["log_file"], maxBytes=10000000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(get_config()["log_format"]))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get specific book by it's ID"""
    app.logger.info("Input: %s", book_id) # [LOGGING]

    response = preprocess_resp(get_book_by("id", DB_ADDRESS, book_id))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    """Return all books with matching names for `author` or `title`"""
    search_query = request.args.get("q", "")

    app.logger.info("Input: %s", search_query) # [LOGGING]

    response = preprocess_resp(get_book_by("author_or_title", DB_ADDRESS, search_query))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    """Returns `n` most similar books to the one which's `id` was passed as URL argument"""
    filters = request.get_json()

    app.logger.info("Input: %s", filters) # [LOGGING]

    base = json.loads(get_book_by("id", DB_ADDRESS, book_id))["resp"][0]
    query = make_query(filters)

    matches = json.loads(db_fetch(DB_ADDRESS, query))["resp"]
    scores = get_candidates(base, matches)

    response = json.dumps(get_sorted(base["metadata"]["title"], scores))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8000, debug=True)

    # for profiling purposes
    book_id = "8331669957f25b1ae217aadaf2a064a33042933c"
    filters = {
        "book": 1234,
        "characters": {
            "aliens": 1,
            "dragons": 0,
            "humanoiddroids": 0,
            "mutants": 0,
            "robots": 0,
            "superintelligence": 0
        },
        "spaceSetting": {
            "beyondsolarsystem": 0,
            "insideearth": 0,
            "otherplanets": 0,
            "outerspace": 0
        },
        "timeSetting": "ALTERNATIVE_TIMELINE",
        "metadata": {
            "genre": {
                "id": 2,
                "type": "genre",
                "value": "Science Fiction",
                "label": "Genre:",
                "state": 0,
                "initial": None
            },
            "country": {
                "id": 3,
                "type": "country",
                "value": "ANY",
                "label": "Country:",
                "state": 2,
                "initial": None
            },
            "author": {
                "id": 1,
                "type": "author",
                "value": "Robert A. Heinlein",
                "label": "Author:",
                "state": 1,
                "initial": None
            }
        }
    }


    base = json.loads(get_book_by("id", DB_ADDRESS, book_id))["resp"][0]
    query = make_query(filters)

    matches = json.loads(db_fetch(DB_ADDRESS, query))["resp"]
    scores = get_candidates(base, matches)
    response = json.dumps(get_sorted(base["metadata"]["title"], scores))
