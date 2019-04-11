import json
import os

dirname = os.path.dirname(__file__)

def escape(s):
    return s.replace("'", "''").strip()

with open(os.path.join(dirname, "all_restaurant_menus.json")) as f:
    restaurant_menus = json.load(f)

sql_strs = []

for restaurant in restaurant_menus:
    restaurant_name = escape(restaurant["name"])
    restaurant_url = escape(restaurant["url"])
    sql_strs.append(
        "INSERT INTO restaurants (name, url) VALUES "
        f"""('{restaurant_name}', '{restaurant_url}');"""
    )

    for menu_category in restaurant["menu"]:
        category = escape(menu_category["title"])

        for menu_item in menu_category["items"]:
            menu_item_name = escape(menu_item["name"])
            menu_item_price = float(menu_item["price"][1:])
            sql_strs.append(
                "INSERT INTO menu_items (name, category, price, restaurant_id) VALUES ("
                f"""'{menu_item_name}', """
                f"""'{category}', """
                f"""{menu_item_price}, """
                f"""(SELECT id FROM restaurants WHERE name = '{restaurant_name}')"""
                ");"
            )

with open(os.path.join(dirname, "all_restaurant_menus.sql"), "w") as f:
    f.write("\n".join(sql_strs))