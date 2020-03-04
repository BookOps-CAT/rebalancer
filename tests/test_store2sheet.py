from datetime import datetime


from context import store2sheet


def test_name_cart():
    assert store2sheet.name_cart() == f'Rebalancing Cart {datetime.now().strftime("%B %Y")}'
