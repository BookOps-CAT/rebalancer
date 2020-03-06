# !!!!
# NEEDS TO BE CLEANED UP AND ORGANIZED BEFORE COMMITTING TO REPO!!!!
import os
import json
from datetime import datetime

from datastore import (
    session_scope,
    Audience,
    Branch, Cart,
    MatCat,
    OverflowItem
)
from datastore_transactions import (
    insert,
    count_records,
    get_relevant_lang_recs,
    retrieve_records_ordered_by_code
)


from adapters.gdrive.credentials import get_access_token
from adapters.gdrive.sheet import (
    create_sheet,
    file2folder,
    customize_shopping_sheet,
    append2sheet,
    update_categories_formatting)
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


def save_cart_info(sheet_id, system_id):
    with session_scope() as session:
        rec = insert(
            session,
            Cart,
            system_id=system_id,
            shopping_cart_id=sheet_id)
        session.flush()
        return(rec.rid)


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


def get_total_number_of_branches(system_id):
    with session_scope() as session:
        branch_count = count_records(session, Branch, system_id=system_id)
        return branch_count


def audience_label_idx():
    with session_scope() as session:
        audn_recs = retrieve_records(session, Audience)
        audn_idx = {a.label: a.rid for a in audn_recs}

        return audn_idx


def populate_branch_tab(creds, system_id, sheet_id):
    data = []
    with session_scope() as session:
        branch_records = retrieve_records_ordered_by_code(
            session, Branch, system_id=system_id)
        for record in branch_records:
            if record.code:
                data.append([record.code])
    append2sheet(creds, sheet_id, 'branch codes', data)


def populate_data_tab(
    creds,
    system_id,
    cart_id,
    sheet_id,
    tab_name,
):

    data = []
    cat_heading_rows = []

    with session_scope() as session:
        row = 0
        audn_idx = audience_label_idx()
        if system_id == 1:
            url = 'http://iii.brooklynpubliclibrary.org/record=b'
        elif system_id == 2:
            url = 'http://ilsstaff.nypl.org/record=b'
        if tab_name == 'World Lang':
            ordered_langs = get_relevant_lang_recs(session, system_id)

            for _, lang_code, lang_label in ordered_langs:

                row += 1
                cat_heading_rows.append(row)
                data.append([lang_label])
                records = get_items4cart(
                    session,
                    system_id,
                    None,
                    None,
                    lang_code=lang_code)

                for r in records:
                    row += 1
                    link = f'=HYPERLINK("{url}{r.bid}", "see")'
                    data.append([
                        None, r.author, r.title, r.call_no,
                        r.pub_date, link, r.iid])
                    update_record(
                        session, OverflowItem, r.rid,
                        cart_id=cart_id)

        else:
            ordered_cats = order_categories(session, system_id, tab_name)
            lang_code = 'eng'

            for mat_cat_id, label in ordered_cats:
                row += 1
                cat_heading_rows.append(row)

                # get and prep record
                data.append([label])
                audn_id = audn_idx[tab_name]
                records = get_items4cart(
                    session,
                    system_id,
                    audn_id,
                    mat_cat_id,
                    lang_code=lang_code)

                for r in records:
                    row += 1
                    link = f'=HYPERLINK("{url}{r.bid}", "see")'
                    data.append([
                        None, r.author, r.title, r.call_no,
                        r.pub_date, link, r.iid])
                    update_record(
                        session, OverflowItem, r.rid,
                        cart_id=cart_id)
    if data:
        append2sheet(creds, sheet_id, tab_name, data)
        update_categories_formatting(
            creds, sheet_id, tab_name, cat_heading_rows)


def create_shopping_cart(system_id):
    """
    Creates a google sheets and approabs and moves it to
    shared folder
    """
    tabs = ['Adults', 'Teens', 'Kids', 'World Lang', 'branch codes']
    creds = get_access_token()
    cart_name = name_cart()
    sheet_id = create_sheet(creds, cart_name, tabs)
    folder_id = get_gdrive_folder_id()
    file2folder(creds, folder_id, sheet_id)
    branch_count = get_total_number_of_branches(system_id)
    customize_shopping_sheet(creds, sheet_id, tabs, branch_count)
    cart_id = save_cart_info(sheet_id, system_id)
    for tab in tabs:
        if tab == 'branch codes':
            populate_branch_tab(creds, system_id, sheet_id)
        else:
            populate_data_tab(creds, system_id, cart_id, sheet_id, tab)
