import bcrypt
import sqlite3
import json

from . import *
from app.irsystem.models.search import find_best_restaurants, find_top_n_menu_items, get_random_item_from_restaurant
from sqlalchemy.sql.expression import func
from flask import redirect, url_for, Response, make_response, session, flash


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
    print(search)
    bizs = list(find_best_restaurants(search)["name"].values)[:5]

    return Response(json.dumps(bizs), mimetype='application/json')


@irsystem.route('/search', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        return redirect(url_for('irsystem.index'))

    bizs = list(find_best_restaurants(query)["name"].values)
    menu_items_df = find_top_n_menu_items(bizs[0])

    menu_items = [
        {
            "name": getattr(row, "name"),
            "price": getattr(row, "price"),
        }
        for row in menu_items_df.itertuples()
    ] if menu_items_df is not None else []

    return render_template(
        'search.html',
        restaurant_name=bizs[0],
        menu_items=menu_items,
    )


@irsystem.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if "session_username" in request.cookies:
            return redirect(url_for('irsystem.index'))

        return render_template(
            'login.html',
        )
    elif request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        if "signup" in request.form:
            try:
                with db:
                    hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt(12))
                    cursor = db.execute(
                        "INSERT INTO users (username, hashed_pw) "
                        "values (:username, :hashed_pw)",
                        {"username": username, "hashed_pw": hashed_pw},
                    )
                    session["session_username"] = username
                    flash("Successfully signed up", "success")
                    return redirect(url_for("irsystem.index"))
            except sqlite3.IntegrityError:
                flash("Username has already been used. Please try again.", "danger")
                return redirect(url_for("irsystem.login"))
        elif "login" in request.form:
            cursor = db.execute(
                "SELECT hashed_pw FROM users WHERE username = :username",
                {"username": username},
            )
            row = cursor.fetchone()

            if row is not None and bcrypt.checkpw(password, row["hashed_pw"]):
                session["session_username"] = username
                flash("Successfully logged in", "success")
                return redirect(url_for("irsystem.index"))
            else:
                flash("Invalid username or password", "danger")
                return redirect(url_for("irsystem.login"))
        else:
            return redirect(url_for('irsystem.login'))


@irsystem.route('/logout', methods=['GET'])
def logout():
    session.pop("session_username", None)
    return redirect(url_for('irsystem.index'))
