from multiprocessing import Pool
import numpy as np
import pandas as pd
import scipy as sp
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
all_yelp_users = np.genfromtxt(data_path("all_yelp_users.csv"), dtype='U22')
all_yelp_users_reverse_index = {
    hash: number for number, hash in enumerate(all_yelp_users.tolist())
}

user_dish_mtx = sp.sparse.load_npz(data_path("user_dish_mtx.npz")).tocsc()


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


def fuzzy_substring(needle, haystack):
    m, n = len(needle), len(haystack)

    # base cases
    if m == 1:
        return needle not in haystack
    if not n:
        return m

    row1 = [0] * (n+1)
    for i in range(0, m):
        row2 = [i+1]
        for j in range(0, n):
            cost = (needle[i] != haystack[j])

            row2.append(min(row1[j+1]+1,  # deletion
                            row2[j]+1,  # insertion
                            row1[j]+cost)  # substitution
                        )
        row1 = row2
    return min(row1)


def find_best_restaurants(query):
    distances = all_restaurants_df["name"].apply(
        lambda n: custom_edit_dist(query, n))
    top_10 = distances.sort_values()[:10]
    return all_restaurants_df.loc[top_10.index]


def get_all_reviews_for_restaurant(restaurant_hash):
    return all_reviews_df[all_reviews_df["restaurant"] == restaurant_hash]

# DEPRECATED
# def build_review_dish_matrix(restaurant_hash, menu):
#     reviews = get_all_reviews_for_restaurant(restaurant_hash)
#     reviews = reviews.reset_index()
#     result = np.zeros([len(reviews), len(menu)])

#     menu_terms = menu["name"].values

#     for rev_ind, review in reviews.iterrows():
#         review_text = review["text"]
#         for term_ind, term in enumerate(menu_terms):
#             # for some reason we have some NaN names?
#             term = str(term)
#             _score = fuzzy_substring(term.lower(), review_text.lower())
#             if _score < min(len(term) / 4, 4):
#                 result[rev_ind][term_ind] = 1
#     return result


# def process_biz_row(biz):
#     res_name = biz[0]
#     res_hash = biz[1]
#     print(res_name)
#     menu = all_menus[all_menus["rest_name"] == res_name]
#     rev_dish_mtx = build_review_dish_matrix(res_hash, menu)
#     return [res_hash, res_name, rev_dish_mtx.tolist()]


# def build_all_review_dish_matrices():
#     p = Pool(3)
#     menu_biz_names = all_menus["rest_name"].unique()
#     ok_restaurants = all_restaurants_df[all_restaurants_df["name"].isin(
#         menu_biz_names)]
#     ok_restaurants = ok_restaurants[["name", "hash"]].values
#     return p.map(process_biz_row, ok_restaurants)


def process_biz_row_into_UD_matrix(biz):
    biz_name = biz[0]
    biz_hash = biz[1]
    print(biz_name)

    reviews = get_all_reviews_for_restaurant(biz_hash)
    result = sp.sparse.lil_matrix((n_users, n_dishes), dtype='b')

    menu = all_menus[all_menus["rest_name"] == biz_name]

    for _, review in reviews.iterrows():
        review_text = review["text"]
        review_author = review["user"]
        author_ind = all_yelp_users_reverse_index[review_author]
        for dish_ind, dish in menu.iterrows():
            # for some reason we have some NaN names?
            term = str(dish["name"])
            _score = fuzzy_substring(term.lower(), review_text.lower())
            if _score < min(len(term) / 4, 4):
                result[author_ind, dish_ind] = 1
    return result


n_users = len(all_yelp_users)
n_dishes = len(all_menus)


def build_user_dish_matrix():
    # global output = sp.sparse.csc_matrix((100, 200), dtype='b')

    p = Pool(3)
    menu_biz_names = all_menus["rest_name"].unique()
    ok_restaurants = all_restaurants_df[all_restaurants_df["name"].isin(
        menu_biz_names)]
    ok_restaurants = ok_restaurants[["name", "hash"]].values
    mapped = p.map(process_biz_row_into_UD_matrix, ok_restaurants)
    return np.array(mapped).sum(axis=0)


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
    # NEEDS TO BE UPDATED
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
        all_menus.loc[all_menus["rest_name"] ==
                      restaurant_name]["name"].sample()
    )[0]

    return restaurant_name, item_name


def get_menu_item_info(menu_item, restaurant):
    """ Returns the menu item's info as a dictionary if it exists, else None. """
    filtered_df = all_menus.loc[
        (all_menus["rest_name"] == restaurant) & (
            all_menus["name"] == menu_item)
    ]

    if filtered_df.empty:
        return None
    else:
        return filtered_df.to_dict("records")[0]


def rest_dish_pair_to_dish_id(obj):
    rest_name = obj["restaurant"]
    dish_name = obj["menuItem"]
    menu = find_best_menu(rest_name)
    if menu is None:
        return None
    dish_row = menu[menu["name"] == dish_name]
    if len(dish_row) == 0:
        return None
    return dish_row.index.item()


def rocchio_top_n(like_indices, dislike_indices, biz_name,
                  n=10, a=.5, b=1, c=1):
    og_query = np.ones((n_users, 1))
    like_emb = user_dish_mtx[:, like_indices]
    if len(like_indices) == 0:
        like_emb = np.zeros((n_users, 1))
    elif np.sum(like_emb) > 0:
        like_emb = np.sum(like_emb, axis=1)

    dislike_emb = user_dish_mtx[:, dislike_indices]
    if len(dislike_indices) == 0:
        dislike_emb = np.zeros((n_users, 1))
    elif np.sum(dislike_emb) > 0:
        dislike_emb = np.sum(dislike_emb, axis=1)
    print(like_emb.sum())

    query_vector = a * og_query + b * like_emb - c * dislike_emb

    biz_menu_df = find_best_menu(biz_name)

    if biz_menu_df is None:
        return None

    biz_menu_ids = biz_menu_df.index.to_numpy()

    def dish_id_to_score(dish_id):
        dish_vector = user_dish_mtx[:, dish_id].todense()
        return sp.spatial.distance.cosine(dish_vector.T, query_vector)

    dish_scores = np.array(list(map(dish_id_to_score, biz_menu_ids)))
    best_dish_idx = dish_scores.argsort()[:n]
    best_dish_ids = biz_menu_ids[best_dish_idx]
    return biz_menu_df.loc[best_dish_ids]
