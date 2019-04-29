import bcrypt
import sqlite3
import json

from . import *
from app.irsystem.models.search import (
    find_best_restaurants,
    get_random_item_from_restaurant,
    get_menu_item_info,
    rest_dish_pair_to_dish_id,
    rocchio_top_n,
    menu_item_edit_dist,
)
from sqlalchemy.sql.expression import func
from flask import (
    redirect,
    url_for,
    Response,
    make_response,
    session,
    flash,
    abort,
    jsonify,
)


@irsystem.route("/", methods=["GET"])
def index():
    restaurant, menu_item = get_random_item_from_restaurant()
    return render_template(
        "index.html", restaurant_suggestion=restaurant, menu_item_suggestion=menu_item
    )


@irsystem.route("/about", methods=["GET"])
def about():
    return render_template(
        "about.html",
        team_members=[
            ("Joseph Chuang", "jcc436"),
            ("Ryan Curtis", "rec284"),
            ("Tyler Ishikawa", "tyi3"),
            ("Danyal Motiwalla", "djm453"),
            ("Jessica Wu", "jlw377"),
        ],
    )


@irsystem.route("/autocomplete", methods=["GET"])
def autocomplete():
    search = request.args.get("term")
    bizs = list(find_best_restaurants(search)["name"].values)[:5]

    return Response(json.dumps(bizs), mimetype="application/json")


@irsystem.route("/search", methods=["POST"])
def search():
    if ("restaurant-name" not in request.form):
        return redirect(url_for("irsystem.index"))

    restaurant = request.form.get("restaurant-name")
    likes = [int(item) for item in request.form.getlist("likes")]
    dislikes = [int(item) for item in request.form.getlist("dislikes")]
    print(restaurant)
    print(likes)
    print(dislikes)

    biz = list(find_best_restaurants(restaurant)["name"].values)[0]
    results, scores = rocchio_top_n(likes, dislikes, biz)

    menu_items = (
        [
            {
                "name": getattr(row, "name"),
                "price": getattr(row, "price"),
                "img": getattr(row, "img"),
                "score": (1 - scores[index]) * 1000 // 1 / 10,
            }
            for index, row in enumerate(results.itertuples())
        ]
        if results is not None
        else []
    )

    return render_template("search.html", restaurant_name=biz, menu_items=menu_items)


@irsystem.route("/api/menu-item", methods=["GET"])
def menu_item_api():
    restaurant = request.args.get("restaurant", None)
    menu_item = request.args.get("menuItem", None)

    if None in (restaurant, menu_item):
        abort(404)

    menu_item_info = get_menu_item_info(menu_item, restaurant)

    if menu_item_info is None:
        abort(404)

    return jsonify(menu_item_info)


@irsystem.route("/api/menu-item/autocomplete", methods=["GET"])
def menu_item_autocomplete():
    restaurant = request.args.get("restaurant", None)
    query = request.args.get("query", "")

    if restaurant is None:
        response = []
    else:
        response = list(menu_item_edit_dist(restaurant, query)["name"].values)[:5]

    return Response(json.dumps(response), mimetype="application/json")
