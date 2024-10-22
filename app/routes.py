from typing import Any, Dict, List

from flask import Blueprint, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> str:
    return render_template("index.html")


@main_bp.route("/api/data")
def get_data() -> List[Dict[str, Any]]:
    # Sample data - replace with your actual data source
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
        {"id": 3, "value": 30},
        {"id": 4, "value": 40},
    ]
    return jsonify(data)
