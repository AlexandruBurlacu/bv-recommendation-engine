"""API module

Here are defined all endpoints of the Recommendation Service API, namely
GET /api/v1/books/<book_id> to get information about a book queried by ID
GET /api/v1/books?q to get books by title or author's name
POST /api/v1/books/<book_id>/recommendations to get book recommendations for a book by ID
"""

import json
from flask import Flask, request

from logic import get_candidates, preprocess_resp
from utils import (get_book_by_id, search_by_auth_or_title,
                   get_config, db_fetch, make_query, get_sorted)

app = Flask(__name__)
addr = get_config()["mongo_rest_interface_addr"]

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get specific book by it's ID"""

    return preprocess_resp(get_book_by_id(addr, book_id))

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    """Return all books with matching names for `author` or `title`"""
    search_query = request.args.get("q", "")

    return preprocess_resp(search_by_auth_or_title(addr, search_query))

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    """Returns 5 most similar books to the one which's `id` was passed as URL argument"""
    filters = request.get_json()["filters"]
    base = json.loads(get_book_by_id(addr, book_id))["resp"][0]
    query = make_query(filters)

    matches = json.loads(db_fetch(addr, query))["resp"]

    scores = get_candidates(base, matches)

    base_title = base["metadata"]["title"]

    return json.dumps(get_sorted(base_title, scores))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
