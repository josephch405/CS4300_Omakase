from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.search import find_best_restaurants, find_best_menu
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sqlalchemy.sql.expression import func


@irsystem.route('/', methods=['GET'])
def index():
    rand_restaurant_name = Restaurant.query.order_by(func.random()).first().name
    return render_template('index.html', restaurant_suggestion=rand_restaurant_name)

@irsystem.route('/search', methods=['GET'])
def search():
    query = request.args.get('search')
    if not query:
        data = []
        output_message = ''
    else:
        bizs = list(find_best_restaurants(query)["name"].values)
        output_message = "Restaurant found: " + bizs[0]
        data = ["No menu items found"]
        menu = find_best_menu(bizs[0])
        if menu is not None:
            data = list(menu["name"].values)
        print(len(data))
    return render_template('index.html',
                           output_message=output_message, data=data)
