from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.search import find_best_restaurants, find_best_menu
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sqlalchemy.sql.expression import func
from flask import redirect, url_for


@irsystem.route('/', methods=['GET'])
def index():
    rand_restaurant_name = Restaurant.query.order_by(func.random()).first().name
    return render_template('index.html', restaurant_suggestion=rand_restaurant_name)

@irsystem.route('/search', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        redirect(url_for('index'))

    bizs = list(find_best_restaurants(query)["name"].values)
    # Restaurant.query.get(name=bizs[0]).

    return render_template(
        'search.html',
        restaurant_name=restaurant_name,
        menu_items=menu_items
    )
