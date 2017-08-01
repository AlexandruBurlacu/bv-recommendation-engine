from flask import Flask, request, jsonify

from logic import get_top_candidates
from utils import get_book_by_id

import json

app = Flask(__name__)

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    return get_book_by_id(str(book_id))

@app.route("/api/v1/books", methods=["GET"])
def list_all_books():
    search_query = request.args.get("q", "")
    return search_query # TODO: search function (db_fetch q)

@app.route("/api/v1/books/<book_id>/recommendations", methods=["POST"])
def recommend(book_id):
    filters = request.get_json() # TODO: data arives as form
    app.logger.debug(filters)
    return "200"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)

