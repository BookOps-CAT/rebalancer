"""
Sierra export parser

Export fields in following order:
    Bibliographic: Record Number
    Bibliographic: Created Date
    Bibliographic: Title
    Bibliographic: Author
    Bibliographic: Call No.
    Bibliographic: Publication Info.
    Item: Record Number
    Item: Created Date
    Item: Location
    Item: Item Type
    Item: OPAC Message
    Item: Last Checkout Date
    Item: Total Checkouts
    Item: Total Renewals


Export formatting:
    Field delimiter: |
    Text qualifier: "
    Repeated field delimiter: ~
    Maximum field length: None

note: call numbers may repeat (branch-research) and only branch ones should be
      considered
"""

from collections import namedtuple, OrderedDict
import csv
from datetime import datetime
import re


from datastore import session_scope, Branch, OverflowItem, ItemType, ShelfCode
from datastore_transactions import create_code_idx, insert

RowData = namedtuple(
    'RowData',
    'bib_id, bib_created_date, title, author, pub_info, call_no, '
    'item_id, item_created_date, location, item_type, '
    'opac_msg, last_out_date, total_checkouts, total_renewals')


DATE_PATTERN = re.compile(r'\d{4}')

NYP_CALL_PATTERNS = OrderedDict(
    lp=re.compile(r'.*LG[\s,-]PRINT\s', re.IGNORECASE),
    ur=re.compile(r'.*URBAN\s', re.IGNORECASE),
    my=re.compile(r'.*MYSTERY\s', re.IGNORECASE),
    we=re.compile(r'.*WESTERN\s', re.IGNORECASE),
    cl=re.compile(r'.*CLASSICS\s', re.IGNORECASE),
    ho=re.compile(r'.*J\sHOLIDAY\s', re.IGNORECASE),
    sf=re.compile(r'.*SCI FI\s|.*SCI-FI\s', re.IGNORECASE),
    rm=re.compile(r'.*ROMANCE\s', re.IGNORECASE),
    gn=re.compile(r'.*GN\sFIC', re.IGNORECASE),
    pi=re.compile(r'.*\sPIC\s', re.IGNORECASE),
    er=re.compile(r'.*J\sE\s', re.IGNORECASE),
    yr=re.compile(r'.*J\sYR\s', re.IGNORECASE),
    fi=re.compile(r'.*FIC\s', re.IGNORECASE),
    bi=re.compile(r'^B\s.*|\sB\s.*', re.IGNORECASE),
    dv=re.compile(r'^DVD\s.*|.*\sDVD\s.*', re.IGNORECASE),
    cd=re.compile(r'^CD\s.*', re.IGNORECASE),
    d0=re.compile(r'^0\d{2}.*|.*\s0\d{2}.*', re.IGNORECASE),
    d1=re.compile(r'^1\d{2}.*|.*\s1\d{2}.*', re.IGNORECASE),
    d2=re.compile(r'^2\d{2}.*|.*\s2\d{2}.*', re.IGNORECASE),
    d3=re.compile(r'^3\d{2}.*|.*\s3\d{2}.*', re.IGNORECASE),
    d4=re.compile(r'^4\d{2}.*|.*\s4\d{2}.*', re.IGNORECASE),
    d5=re.compile(r'^5\d{2}.*|.*\s5\d{2}.*', re.IGNORECASE),
    d6=re.compile(r'^6\d{2}.*|.*\s6\d{2}.*', re.IGNORECASE),
    d7=re.compile(r'^7\d{2}.*|.*\s7\d{2}.*', re.IGNORECASE),
    d8=re.compile(r'^8\d{2}.*|.*\s8\d{2}.*', re.IGNORECASE),
    d9=re.compile(r'^9\d{2}.*|.*\s9\d{2}.*', re.IGNORECASE),
)


def prep_ids(sierra_id):
    try:
        return int(sierra_id[1:-1])
    except TypeError:
        return
    except ValueError:
        return


def determine_branch_id(location, branch_idx):
    code = location[:2].lower()
    if code in branch_idx:
        return branch_idx[code]
    else:
        return branch_idx[None]


def parse_pub_date(pub_info):
    try:
        match = DATE_PATTERN.search(pub_info)
        if match:
            return match.group(0)
    except TypeError:
        return


def string2date(date_string):
    try:
        return datetime.strptime(date_string[:10], '%m-%d-%Y').date()
    except TypeError:
        return
    except ValueError:
        return


def determine_nyp_mat_cat(call_no):
    # call_no =
    for p, v in NYP_CALL_PATTERNS.items():
        m = v.search(call_no)
        if m:
            return p


def get_mat_cat_id(call_no, opac_msg, system_id):
    if system_id == 1:
        # BPL
        pass
    elif system_id == 2:
        # NYPL
        mat_cat = determine_nyp_mat_cat(call_no)


def sierra_export_reader(fh):
    reader = csv.reader(
        open(fh, 'r', encoding='utf-8', newline=''),
        delimiter='|',
        quotechar='"')

    # skip header
    next(reader)

    for row in map(RowData._make, reader):
        yield row


def save2store(fh, system_id):
    data = sierra_export_reader(fh)
    with session_scope() as session:
        branch_idx = create_code_idx(session, Branch, system_id=system_id)
        for k, v in branch_idx.items():
            print(k, v)

        for element in data:

            overflow_item = dict(
                system_id=system_id,
                bib_id=prep_ids(element.bib_id),
                item_id=prep_ids(element.item_id),
                src_branch_id=determine_branch_id(element.location, branch_idx),
                pub_date=parse_pub_date(element.pub_info),
                bib_created_date=string2date(element.bib_created_date),
                item_created_date=string2date(element.item_created_data),
                mat_cat_id=None
                )


            # session.commit()




# def find_nth_value(field, n):
#     return field.split('~')[n]


# def determine_mat_category(call_no):
#     call_no = find_nth_value(call_no, 0)
#     for p, v in CALL_PATTERNS.items():
#         m = v.search(call_no)
#         if m:
#             return p


# def determine_audience_id(location):
#     try:
#         audn_id = AUDN_CODES[location[2]][0]
#     except KeyError:
#         # eng code id is 4
#         audn_id = 4
#     return audn_id


# def determine_language(call_no):
#     # J-FRE PIC ADAMS add pattern handling
#     found = False
#     for code in LANG_CODES.keys():
#         if code in call_no.lower().split(' '):
#             found = True
#             break
#     if found:
#         return code
#     else:
#         return 'eng'



# def determine_item_type_id(session, code):
#     res = retrieve_record(
#         session,
#         ItemType,
#         code=code.strip())

#     if res:
#         item_type_id = res.sid
#     else:
#         res = insert_or_ignore(
#             session,
#             ItemType,
#             code=code.strip())
#         session.flush()
#         item_type_id = res.sid

#     return item_type_id



