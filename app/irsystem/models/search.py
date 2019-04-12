import numpy as np
import pandas as pd
import nltk
import os
from app import db
from .data_models import Restaurant, MenuItem


def custom_edit_dist(q, restaurant_name):
    q_parts = q.split()
    restaurant_parts = restaurant_name.split()

    r_p_scores = list(map(lambda n: min(
        map(lambda q: nltk.edit_distance(n.lower(), q.lower()), q_parts)
    ), restaurant_parts))

    final_score = min(r_p_scores) + max(r_p_scores) * 0.01

    return final_score


def find_best_restaurants(query):
    restaurant_names_df = pd.DataFrame(
        {"name": [r.name for r in Restaurant.query.all()]}
    )
    distances = restaurant_names_df["name"].apply(
        lambda n: custom_edit_dist(query, n)
    )
    top_10 = distances.sort_values()[:10]
    return restaurant_names_df.loc[top_10.index]


def find_best_menu(restaurant_name):
    menu_biz_names_list = MenuItem.query.join(Restaurant).with_entities(Restaurant.name).distinct()
    menu_biz_names = np.array([m.name for m in menu_biz_names_list])

    # found direct match, return
    if restaurant_name not in menu_biz_names:
        # search for close-enough restaurant name
        distances = list(map(lambda n: custom_edit_dist(restaurant_name, n),
                             menu_biz_names))
        top_10 = np.argsort(distances)[:10]
        if distances[top_10[0]] > 2:
            return None
        restaurant_name = menu_biz_names[top_10][0]
    # we keep intermediary 10 best menus just in case, can refactor
    menu_items = MenuItem.query.join(Restaurant).filter(Restaurant.name == restaurant_name)
    return pd.DataFrame({"name": [m.name for m in menu_items]})
