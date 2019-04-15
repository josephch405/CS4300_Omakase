from . import *
from app.irsystem.models.search import find_best_restaurants, find_best_menu, get_random_restaurant
from sqlalchemy.sql.expression import func
from flask import redirect, url_for, Response, make_response, session, flash


@irsystem.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        restaurant_suggestion=get_random_restaurant(),
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
    menu_items_df = find_best_menu(bizs[0])
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
        username = request.form.get("username")
        password = request.form.get("password")

        session["session_username"] = username

        return redirect(url_for('irsystem.index'))

@irsystem.route('/logout', methods=['GET'])
def logout():
    session.pop("session_username", None)
    return redirect(url_for('irsystem.index'))
