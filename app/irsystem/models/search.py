import numpy as np
import pandas as pd
import nltk
import os


def csv_path(n):
    return os.path.join(os.path.dirname(__file__), n)


all_reviews_df = pd.read_csv(
    csv_path("all_reviews.csv"), encoding="unicode_escape")
all_restaurants_df = pd.read_csv(
    csv_path("all_restaurants.csv"), encoding="unicode_escape")
all_menus = pd.read_csv(
    csv_path("all_menus.csv"), encoding="unicode_escape")


def custom_edit_dist(q, restaurant_name):
    q_parts = q.split()
    restaurant_parts = restaurant_name.split()

    r_p_scores = list(map(lambda n: min(
        map(lambda q: nltk.edit_distance(n.lower(), q.lower()), q_parts)
    ), restaurant_parts))

    final_score = min(r_p_scores)

    return final_score


def find_best_restaurants(query):
    distances = all_restaurants_df["name"].apply(
        lambda n: custom_edit_dist(query, n))
    top_10 = distances.sort_values()[:10]
    # print(top_10)
    # print(all_restaurants_df.loc[top_10.index])
    return all_restaurants_df.loc[top_10.index]
