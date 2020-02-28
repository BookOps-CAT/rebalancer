# !!!!
# NEEDS TO BE CLEANED UP AND ORGANIZED BEFORE COMMITTING TO REPO!!!!
import os
import json
from datetime import datetime

from datastore import session_scope, Cart, Hold
from datastore_transactions import get_items4cart, insert, update_record
from data.categories import CATS_BY_AUDN
from data.audiences import AUDN_CODES
from data.languages import LANG_CODES


from adapters.gdrive.credentials import get_access_token
from adapters.gdrive.sheet import (create_sheet, file2folder,
                                   customize_shopping_sheet,
                                   append2sheet, update_categories_formatting)


def get_gdrive_folder_id():
    """
    returns rebalancing project google drive folder id
    """
    ids_fh = os.path.join(
        os.environ['USERPROFILE'],
        '.google/rebalance_doc_ids.json')
    with open(ids_fh, 'r') as json_file:
        ids = json.load(json_file)
        return ids['folder_id']


def name_cart():
    return f'Rebalancing Cart {datetime.now().strftime("%b %y")}'


def save_cart_id(sheet_id):
    with session_scope() as session:
        rec = insert(
            session, Cart,
            google_sheet_id=sheet_id)
        session.flush()
        return(rec.sid)


def populate_tab(creds, cart_id, sheet_id, tab_name, lang):
    if tab_name == 'Adult':
        audn_id = AUDN_CODES['a'][0]
    elif tab_name == 'Teens':
        audn_id = AUDN_CODES['y'][0]
    elif tab_name == 'Kids':
        audn_id = AUDN_CODES['j'][0]
    elif tab_name == 'WL':
        pass
    else:
        raise AttributeError('Invalid tab provided')

    lang_id = LANG_CODES['eng'][0]

    data = []
    cat_heading_rows = []

    with session_scope() as session:
        row = 0
        for cat_id, label in CATS_BY_AUDN[tab_name].items():
            row += 1
            cat_heading_rows.append(row)
            records = []
            if tab_name == 'WL':
                # WL must have it's own datastore query
                # group by language, then category
                # each language should have additional heading
                # data.append(label)
                # for audn_id in AUDN_CODES.keys()
                pass
            else:
                data.append([label])
                records = get_items4cart(session, audn_id, cat_id, lang_id)
            for r in records:
                row += 1
                data.append([
                    None, r.author, r.title, r.call_no,
                    r.pub_info, r.subject, r.iid])
                update_record(
                    session, Hold, r.hold_id,
                    cart_id=cart_id,
                    outstanding=False)
    if data:
        append2sheet(creds, sheet_id, tab_name, data)
        update_categories_formatting(
            creds, sheet_id, tab_name, cat_heading_rows)


def create_shopping_cart():
    """
    creates a google spreadsheets and its tabs and moves it to
    shared folder
    """
    tabs = ['Adult', 'Teens', 'Kids', 'WL']
    creds = get_access_token()
    cart_name = name_cart()
    sheet_id = create_sheet(creds, cart_name, tabs)
    folder_id = get_gdrive_folder_id()
    file2folder(creds, folder_id, sheet_id)
    customize_shopping_sheet(creds, sheet_id, tabs)
    cart_id = save_cart_id(sheet_id)
    for tab in tabs:
        populate_tab(creds, cart_id, sheet_id, tab, 'eng')
