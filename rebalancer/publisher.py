from adapters.sierra2store import save2store
from adapters.store2sheet import create_shopping_cart


def publish_rebalancing_items(fh):
    save2store(fh)
    create_shopping_cart()


if __name__ == '__main__':
    fh = './temp/sierra-export-3.txt'
    publish_rebalancing_items(fh)
