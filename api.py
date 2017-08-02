"""API module

Here are defined all endpoints of the Recommendation Service API, namely
GET /api/v1/books/<book_id> to get information about a book queried by ID
GET /api/v1/books?q to get books by title or author's name
POST /api/v1/books/<book_id>/recommendation to get book recommendation for a book by ID
"""

from flask import Flask, request, jsonify

from logic import get_top_candidates
from utils import get_book_by_id, search_by_auth_or_title

app = Flask(__name__)

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    return get_book_by_id(book_id), 200, {"Content-Type": "application/json"}

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    search_query = request.args.get("q", "")
    return search_by_auth_or_title(search_query), 200, {"Content-Type": "application/json"}

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    filters = request.get_json()
    return "200", 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(debug=True)
