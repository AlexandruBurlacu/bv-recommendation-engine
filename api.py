"""API module

Here are defined all endpoints of the Recommendation Service API, namely
GET /api/v1/books/<book_id> to get information about a book queried by ID
GET /api/v1/books?q to get books by title or author's name
POST /api/v1/books/<book_id>/recommendations to get book recommendations for a book by ID
"""

from flask import Flask, request, jsonify

from logic import get_top_candidates
from utils import (get_book_by_id, search_by_auth_or_title,
                   get_config, db_fetch, make_query)

app = Flask(__name__)
config = get_config()

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    """Get specific book by it's ID"""
    return jsonify(get_book_by_id(config["mongo_rest_interface_addr"], book_id))

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    """Return all books with matching names for `author` or `title`"""
    search_query = request.args.get("q", "")
    return jsonify(search_by_auth_or_title(config["mongo_rest_interface_addr"], search_query))

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    filters = request.get_json()
    base = get_book_by_id(config["mongo_rest_interface_addr"], book_id)

    query = make_query(filters)
    matches = db_fetch(config["mongo_rest_interface_addr"], query)

    return jsonify(get_top_candidates(base, matches))


if __name__ == "__main__":
    app.run(debug=True)
