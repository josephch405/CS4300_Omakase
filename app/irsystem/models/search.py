from multiprocessing import Pool
import numpy as np
import pandas as pd
import nltk
import os
import json


def data_path(n):
    return os.path.join(os.path.dirname(__file__), n)


all_reviews_df = pd.read_csv(
    data_path("all_reviews.csv"), encoding="unicode_escape")
all_restaurants_df = pd.read_csv(
    data_path("all_restaurants.csv"), encoding="unicode_escape")
all_menus = pd.read_csv(
    data_path("all_menus.csv"), encoding="unicode_escape")
with open(data_path("rev_menu_mtx.json")) as infile:
    rev_menu_mtx_list = json.load(infile)


def custom_edit_dist(q, item):
    # q is the query, ie. "Saigo kitch"
    # item is the target, ie. "Saigon Kitchen"
    q_parts = q.split()
    item_parts = item.split()

    r_p_scores = list(map(lambda n: min(
        map(lambda q: nltk.edit_distance(n.lower(), q.lower()), q_parts)
    ), item_parts))

    final_score = min(r_p_scores) + max(r_p_scores) * 0.01

    return final_score


def find_best_restaurants(query):
    distances = all_restaurants_df["name"].apply(
        lambda n: custom_edit_dist(query, n))
    top_10 = distances.sort_values()[:10]
    return all_restaurants_df.loc[top_10.index]


def get_all_reviews_for_restaurant(restaurant_hash):
    return all_reviews_df[all_reviews_df["restaurant"] == restaurant_hash]


def build_review_dish_matrix(restaurant_hash, menu):
    reviews = get_all_reviews_for_restaurant(restaurant_hash)
    reviews = reviews.reset_index()
    result = np.zeros([len(reviews), len(menu)])

    menu_terms = menu["name"].values

    for rev_ind, review in reviews.iterrows():
        review_text = review["text"]
        review_tokens = review_text.split()
        for term_ind, term in enumerate(menu_terms):
            # for some reason we have some NaN names?
            term = str(term)
            term_wordcount = len(term.split())
            i = 0
            while i + term_wordcount <= len(review_tokens):
                _substring = review_tokens[i:i+term_wordcount]
                _substring = " ".join(_substring)
                _score = nltk.edit_distance(term.lower(), _substring.lower())
                if _score < min(len(term) / 4, 3):
                    result[rev_ind][term_ind] = 1
                    break
                i += 1
    return result


def process_biz_row(biz):
    res_name = biz[0]
    res_hash = biz[1]
    print(res_name)
    menu = all_menus[all_menus["rest_name"] == res_name]
    rev_dish_mtx = build_review_dish_matrix(res_hash, menu)
    return [res_hash, res_name, rev_dish_mtx.tolist()]


def build_all_review_dish_matrices():
    p = Pool(3)
    menu_biz_names = all_menus["rest_name"].unique()
    ok_restaurants = all_restaurants_df[all_restaurants_df["name"].isin(
        menu_biz_names)]
    ok_restaurants = ok_restaurants[["name", "hash"]].values
    return p.map(process_biz_row, ok_restaurants)


def get_rev_dish_matrix_for_name(restaurant_name):
    for biz in rev_menu_mtx_list:
        if biz[1] == restaurant_name:
            return np.array(biz[2])
    return None


def find_best_menu(restaurant_name):
    menu_biz_names = all_menus["rest_name"].unique()

    # found direct match, return
    if restaurant_name not in menu_biz_names:
        # search for close-enough restaurant name
        distances = list(map(lambda n: nltk.edit_distance(restaurant_name, n),
                             menu_biz_names))
        top_10 = np.argsort(distances)[:10]
        if distances[top_10[0]] > 2:
            return None
        restaurant_name = menu_biz_names[top_10][0]
    # we keep intermediary 10 best menus just in case, can refactor
    return all_menus[all_menus["rest_name"] == restaurant_name]


def find_top_n_menu_items(restaurant_name, n=20):
    menu = find_best_menu(restaurant_name)
    rev_dish_mtx = get_rev_dish_matrix_for_name(restaurant_name)

    if rev_dish_mtx is None:
        return None

    dish_scores = rev_dish_mtx.sum(axis=0)

    best_dish_idx = (-1 * dish_scores).argsort()[:n]
    return menu.iloc[best_dish_idx]


def get_random_item_from_restaurant():
    restaurant_name = list(all_menus['rest_name'].sample())[0]
    item_name = list(
        all_menus.loc[all_menus["rest_name"] == restaurant_name]["name"].sample()
    )[0]

    return restaurant_name, item_name