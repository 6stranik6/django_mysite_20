from csv import DictReader
from io import TextIOWrapper
from itertools import product

from shopapp.models import Product, Order


def save_csv_produts(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]

    Product.objects.bulk_create(products)
    return products


def convert_str_to_int_list(string_data):
    chars = ["[", "]", ","]
    filtered_str = filter(lambda c: c not in chars, string_data)
    list_str = "".join(filtered_str)
    list_int = list(map(int, list_str))
    return list_int


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)
    orders = []
    for row in reader:
        order = Order(
            delivery_address=row["delivery_address"],
            promocode=row["promocode"],
            user_id = row["user_id"],
        )
        order.save()
        for product in convert_str_to_int_list(row["product"]):
            order.products.add(product)
        orders.append(order)

    return orders
