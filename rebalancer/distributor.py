from datastore import session_scope, Cart, Hold, Branch
from datastore_transactions import (retrieve_last_record, retrieve_records,
                                    retrieve_record)
from adapters.sheet2store import set_new_branch
from adapters.sierra.session import SierraSession


def get_latest_cart_record():
    # retrieve last entered cart
    with session_scope() as session:
        rec = retrieve_last_record(session, Cart)
        session.expunge(rec)
        return rec


def parse_cart_selections(tabs, sheet_id=None):
    if sheet_id is None:
        sheet_id = get_latest_cart_record().google_sheet_id
    set_new_branch(tabs, sheet_id)


def issue_holds(api_url, sierra_key, sierra_secret, account_id, cart_id=None):
    if cart_id is None:
        cart_id = get_latest_cart_record().sid
    with SierraSession(api_url, sierra_key, sierra_secret) as ils_session:
        with session_scope() as db_session:
            recs = retrieve_records(
                db_session, Hold,
                cart_id=cart_id,
                outstanding=False,
                issued=True)

            for rec in recs:
                if rec.dst_branch_id != 1:
                    dst_branch = retrieve_record(
                        db_session, Branch, sid=rec.dst_branch_id)
                    response = ils_session.hold_place_on_item(
                        account_id, rec.item_id, dst_branch.code)
                    print(
                        f'i{rec.item_id}a,{rec.dst_branch_id},{dst_branch.code},{response.status_code},{response.text}')
                else:
                    print(f'i{rec.item_id}a,{rec.dst_branch_id},None,,')
