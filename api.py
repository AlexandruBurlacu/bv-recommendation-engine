"""API module

Here are defined all endpoints of the Recommendation Service API, namely
GET /api/v1/books/<book_id> to get information about a book queried by ID
GET /api/v1/books?q to get books by title or author's name
POST /api/v1/books/<book_id>/recommendations to get book recommendations for a book by ID
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request

from logic import get_candidates
from utils import (get_book_by_id, search_by_auth_or_title, preprocess_resp,
                   get_config, db_fetch, make_query, get_sorted)

app = Flask(__name__)

addr = get_config()["mongo_rest_interface_addr"]

handler = RotatingFileHandler('logs/info.log', maxBytes=10000000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    "[%(asctime)s] {%(funcName)s in %(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get specific book by it's ID"""
    app.logger.info("Input: {}".format(book_id)) # [LOGGING]

    response = preprocess_resp(get_book_by_id(addr, book_id))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    """Return all books with matching names for `author` or `title`"""
    search_query = request.args.get("q", "")

    app.logger.info("Input: {}".format(search_query)) # [LOGGING]

    response = preprocess_resp(search_by_auth_or_title(addr, search_query))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    """Returns 5 most similar books to the one which's `id` was passed as URL argument"""
    filters = request.get_json()

    app.logger.info("Input: {}".format(filters)) # [LOGGING]

    base = json.loads(get_book_by_id(addr, book_id))["resp"][0]
    query = make_query(filters)

    matches = json.loads(db_fetch(addr, query))["resp"]
    scores = get_candidates(base, matches)

    base_title = base["metadata"]["title"]
    response = json.dumps(get_sorted(base_title, scores))

    app.logger.info("Output: 200 OK") # [LOGGING]
    return response, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
