# !!!!
# NEEDS TO BE CLEANED UP AND ORGANIZED BEFORE COMMITTING TO REPO!!!!
import os
import json
from datetime import datetime

from datastore import session_scope, Cart, MatCat
from datastore_transactions import insert


from adapters.gdrive.credentials import get_access_token
from adapters.gdrive.sheet import (
    create_sheet,
    file2folder,
    customize_shopping_sheet)
#   append2sheet, update_categories_formatting)
from datastore_transactions import (
    get_items4cart,
    retrieve_records,
    update_record)


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
    return f'Rebalancing Cart {datetime.now().strftime("%B %Y")}'


def save_cart_id(sheet_id, system_id):
    with session_scope() as session:
        rec = insert(
            session,
            Cart,
            system_id,
            google_sheet_id=sheet_id)
        session.flush()
        return(rec.sid)


def order_categories(session, system_id, tab):
    """
    Orders material categories to be displayed in each tab
    Returns:
        list of tuples: (mat_cat.rid, mat_cat.label)
    """
    ordered_cats = []
    recs = retrieve_records(session, MatCat, system_id=system_id)
    if tab == 'Adults':
        cats = {r.adults_order: (r.rid, r.label) for r in recs if r.adults_order is not None}
    elif tab == 'Teens':
        cats = {r.teens_order: (r.rid, r.label) for r in recs if r.teens_order is not None}
    elif tab == 'Kids':
        cats = {r.kids_order: (r.rid, r.label) for r in recs if r.kids_order is not None}
    elif tab == 'World Lang':
        cats = {r.wls_order: (r.rid, r.label) for r in recs if r.wls_order is not None}
    ordered_cats = [(cats[v]) for v in sorted(cats.keys())]
    return ordered_cats


def populate_tab(creds, system_id, cart_id, sheet_id, tab_name, lang):
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
            if tab_name == 'World Lang':
                # WL must have it's own datastore query
                # group by language, then category
                # each language should have additional heading
                # data.append(label)
                # for audn_id in AUDN_CODES.keys()
                pass
            else:
                data.append([label])
                records = get_items4cart(
                    session,
                    system_id,
                    audn_id,
                    mat_cat_id,
                    english_lang=english_lang)
            for r in records:
                row += 1
                data.append([
                    None, r.author, r.title, r.call_no,
                    r.pub_info, r.subject, r.iid])
                update_record(
                    session, Hold, r.hold_id,
                    cart_id=cart_id)
    if data:
        # append2sheet(creds, sheet_id, tab_name, data)
        # update_categories_formatting(
        #     creds, sheet_id, tab_name, cat_heading_rows)
        pass


def create_shopping_cart(system_id):
    """
    Creates a google sheets and approabs and moves it to
    shared folder
    """
    tabs = ['Adult', 'Teens', 'Kids', 'World Lang', 'Locations']
    creds = get_access_token()
    cart_name = name_cart()
    sheet_id = create_sheet(creds, cart_name, tabs)
    folder_id = get_gdrive_folder_id()
    file2folder(creds, folder_id, sheet_id)
    customize_shopping_sheet(creds, sheet_id, tabs)
    cart_id = save_cart_id(sheet_id, system_id)
    # for tab in tabs:
    #     populate_tab(creds, cart_id, sheet_id, tab, 'eng')
