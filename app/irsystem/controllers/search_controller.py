from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.search import find_best_restaurants, find_best_menu
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sqlalchemy.sql.expression import func
from flask import redirect, url_for


@irsystem.route('/', methods=['GET'])
def index():
    rand_restaurant_name = Restaurant.query.order_by(func.random()).first().name
    return render_template(
        'index.html',
        restaurant_suggestion=rand_restaurant_name,
        urls={
            'index': url_for('irsystem.index'),
            'search': url_for('irsystem.search'),
        }
    )

@irsystem.route('/search', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        return redirect(url_for('irsystem.index'))

    bizs = list(find_best_restaurants(query)["name"].values)
    menu_items = MenuItem.query.join(Restaurant).filter(Restaurant.name == bizs[0])

    return render_template(
        'search.html',
        restaurant_name=bizs[0],
        menu_items=menu_items,
        urls={
            'index': url_for('irsystem.index'),
            'search': url_for('irsystem.search'),
        },
    )
