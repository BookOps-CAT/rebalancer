import json

from adapters.sierra.session import SierraSession
from adapters.sierra.credentials import get_sierra_creds
from distributor import issue_holds, parse_cart_selections


def get_hold_data(pid):
    base, key, secret = get_sierra_creds()

    with SierraSession(base, key, secret) as session:
        res = session.hold_get_all(pid, limit=300)
        res = res.json()
        with open(f'./temp/account-{pid}-holds.json', 'w') as jsonfile:
            json.dump(res, jsonfile, indent=4)
        print(res)


def delete_holds_from_account(pid):
    base, key, secret = get_sierra_creds()
    with SierraSession(base, key, secret) as session:
        res = session.hold_delete_all(pid)
        return res


def parse_sorter_test_shopping_cart(tabs, sheet_id):
    parse_cart_selections(tabs, sheet_id)


def place_sorter_test_holds(pid, cart_id):
    base, key, secret = get_sierra_creds()
    issue_holds(base, key, secret, pid, cart_id)


if __name__ == '__main__':
    tabs = ['Adult', 'YA', 'Kids']
    sorter_test_sheet_id = 'google sheet id here'
    sorter_test_cart_id = 1
    pid = 'int, account # here'
    parse_sorter_test_shopping_cart(tabs, sorter_test_sheet_id)
    place_sorter_test_holds(pid, sorter_test_cart_id)
    # get_hold_data(pid)
