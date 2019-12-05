from googleapiclient import discovery

from adapters.gdrive.credentials import get_access_token
from data.branches import BRANCH_CODES
from datastore import Hold, session_scope
from datastore_transactions import retrieve_record, update_record


def set_new_branch(tabs, sheet_id):
    """
    Parses shopping cart with provided google sheet id and
    updates dst_branch_id column in hold table of the datastore based on staff
    selection
    args:
        tabs: list of str, list of names of google sheets in the spreadsheet
        sheet_id: str, google sheet id
    """
    creds = get_access_token()
    service = discovery.build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    for tab in tabs:
        results = sheet.values().get(
            spreadsheetId=sheet_id,
            range=tab).execute()

        values = results.get('values', [])
        for row in values[1:]:
            iid = None
            try:
                iid = int(row[6])

                # find row with actual data
                if iid:
                    try:
                        loc_code = row[7]
                        dst_branch_id = BRANCH_CODES[loc_code][0]
                    except IndexError:
                        dst_branch_id = BRANCH_CODES[None][0]
                    # print(f'dst_id:{dst_branch_id}')
            except IndexError:
                # row with no data (example a section heading row)
                pass
            except ValueError:
                # log as error or warning
                pass

            if iid is not None:
                with session_scope() as session:
                    hold_rec = retrieve_record(
                        session, Hold, item_id=iid,
                        outstanding=False, issued=False)
                    if hold_rec:
                        update_record(
                            session, Hold, hold_rec.sid,
                            dst_branch_id=dst_branch_id,
                            issued=True)
