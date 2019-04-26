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
from flask import redirect, url_for, Response, make_response, session, flash, abort


@irsystem.route('/', methods=['GET'])
def index():
    restaurant, menu_item = get_random_item_from_restaurant()
    return render_template(
        'index.html',
        restaurant_suggestion=restaurant,
        menu_item_suggestion=menu_item,
    )


@irsystem.route('/about', methods=['GET'])
def about():
    return render_template(
        'about.html',
        team_members=[
            ("Joseph Chuang", "jcc436"),
            ("Ryan Curtis", "rec284"),
            ("Tyler Ishikawa", "tyi3"),
            ("Danyal Motiwalla", "djm453"),
            ("Jessica Wu", "jlw377"),
        ]
    )


@irsystem.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('term')
    bizs = list(find_best_restaurants(search)["name"].values)[:5]

    return Response(json.dumps(bizs), mimetype='application/json')


@irsystem.route('/search', methods=['POST'])
def search():
    if "preferences" not in request.form:
        return redirect(url_for('irsystem.index'))

    preferences = json.loads(request.form.get("preferences"))

    restaurant = preferences["restaurant"]
    likes = preferences["likes"]
    dislikes = preferences["dislikes"]

    likes = list(map(rest_dish_pair_to_dish_id, likes))
    dislikes = list(map(rest_dish_pair_to_dish_id, dislikes))

    biz = list(find_best_restaurants(restaurant)["name"].values)[0]
    results, scores = rocchio_top_n(likes, dislikes, biz)

    menu_items = [
        {
            "name": getattr(row, "name"),
            "price": getattr(row, "price"),
        }
        for row in results.itertuples()
    ] if results is not None else []

    menu_items = map(lambda t: {
        "name": t[1]["name"],
        "price": t[1]["price"],
        "score": (1 - scores[t[0]]) * 1000 // 1 / 10
    }, enumerate(menu_items))

    return render_template(
        'search.html',
        restaurant_name=biz,
        menu_items=menu_items,
    )


@irsystem.route('/api/menu-item', methods=['GET'])
def menu_item_api():
    restaurant = request.args.get('restaurant', None)
    menu_item = request.args.get('menuItem', None)

    if None in (restaurant, menu_item):
        abort(404)

    menu_item_info = get_menu_item_info(menu_item, restaurant)

    if menu_item_info is None:
        abort(404)

    return Response(json.dumps(menu_item_info), mimetype='application/json')


@irsystem.route('/api/menu-item/autocomplete', methods=['GET'])
def menu_item_autocomplete():
    restaurant = request.args.get("restaurant", None)
    query = request.args.get("query", "")

    if restaurant is None:
        response = []
    else:
        response = list(menu_item_edit_dist(
            restaurant, query)["name"].values)[:5]

    return Response(json.dumps(response), mimetype='application/json')
