"""
Sierra export parser

Export fields in following order:
    Type: Field
    Item: Record Number
    Bibliographic: Record Number
    Bibliographic: Author
    Bibliographic: Title
    Bibliographic: Publication Info.
    Bibliographic: Call No.
    Bibliographic: Subject
    Item: Item Type
    Item: Total Checkouts
    Item: Last Checkout Date
    Item: Location
    Item: Status

Export formatting:
    Field delimiter: ^
    Text qualifier: None
    Repeated field delimiter: ~
    Maximum field length: None

note: call numbers may repeat (branch-research) and only branch ones should be
      considered
"""

from collections import namedtuple, OrderedDict
import csv
from datetime import datetime
import re


from datastore import session_scope, Bib, Item, ItemType, Status, Shelf, Hold
from datastore_transactions import (insert, insert_or_ignore, insert_or_update, retrieve_record)
from data.audiences import AUDN_CODES
from data.branches import BRANCH_CODES
from data.languages import LANG_CODES
from data.categories import REBALANCE_CATS
from data.status import STATUS_CODES


RowData = namedtuple(
    'RowData',
    'iid, bid, author, title, pub_info, call_no, subject, item_type, '
    'checkouts, last_checkout, location, status')

BibData = namedtuple(
    'BibData',
    'sid, author, title, pub_info, call_no, subject, mat_cat_id, '
    'audn_id, lang_id')

ItemData = namedtuple(
    'ItemData',
    'sid, bib_id, status_id, item_type_id, checkouts, '
    'last_checkout')


CALL_PATTERNS = OrderedDict(
    ur=re.compile(r'.*URBAN\s', re.IGNORECASE),
    my=re.compile(r'.*MYSTERY\s', re.IGNORECASE),
    we=re.compile(r'.*WESTERN\s', re.IGNORECASE),
    cl=re.compile(r'.*CLASSICS', re.IGNORECASE),
    sf=re.compile(r'.*SCI FI\s', re.IGNORECASE),
    rm=re.compile(r'.*ROMANCE\s', re.IGNORECASE),
    gn=re.compile(r'.*GN\sFIC', re.IGNORECASE),
    pi=re.compile(r'.*\sPIC\s', re.IGNORECASE),
    er=re.compile(r'.*J\sE\s', re.IGNORECASE),
    yr=re.compile(r'.*J\sYR\s', re.IGNORECASE),
    fi=re.compile(r'.*FIC\s', re.IGNORECASE),
    bi=re.compile(r'^B\s.*|\sB\s.*', re.IGNORECASE),
    dv=re.compile(r'^DVD\s.*|.*\sDVD\s.*', re.IGNORECASE),
    cd=re.compile(r'^CD\s.*', re.IGNORECASE),
    pe=re.compile(r'^PER|.*\sPER', re.IGNORECASE),
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
    return int(sierra_id[1:-1])


def find_nth_value(field, n):
    return field.split('~')[n]


def determine_mat_category(call_no):
    call_no = find_nth_value(call_no, 0)
    for p, v in CALL_PATTERNS.items():
        m = v.search(call_no)
        if m:
            return p


def determine_audience_id(location):
    try:
        audn_id = AUDN_CODES[location[2]][0]
    except KeyError:
        # eng code id is 4
        audn_id = 4
    return audn_id


def determine_language(call_no):
    found = False
    for code in LANG_CODES.keys():
        if code in call_no.lower().split(' '):
            found = True
            break
    if found:
        return code
    else:
        return 'eng'


def determine_branch_id(location):
    code = location[:2].lower()
    if code in BRANCH_CODES.keys():
        return BRANCH_CODES[code][0]
    else:
        return BRANCH_CODES[None][0]


def normalize_date(date_string):
    if date_string[0] == ' ':
        return None
    else:
        return datetime.strptime(date_string[:10], '%m-%d-%Y')


def determine_status_id(code):
    if code in STATUS_CODES.keys():
        return STATUS_CODES[code][0]
    else:
        return STATUS_CODES[None][0]


def determine_item_type_id(session, code):
    res = retrieve_record(
        session,
        ItemType,
        code=code.strip())

    if res:
        item_type_id = res.sid
    else:
        res = insert_or_ignore(
            session,
            ItemType,
            code=code.strip())
        session.flush()
        item_type_id = res.sid

    return item_type_id


def determine_shelf_id(session, location):
    code = location[2:].strip()
    res = retrieve_record(
        session,
        Shelf,
        code=code)
    if res:
        return res.sid
    else:
        res = insert_or_ignore(
            session,
            Shelf,
            code=code)
        session.flush()
        return res.sid


def sierra_export_reader(fh):
    reader = csv.reader(
        open(fh, 'r', encoding='utf-8', newline=''),
        delimiter='^',
        quoting=csv.QUOTE_NONE)

    # skip header
    next(reader)

    for row in map(RowData._make, reader):
        yield row


def save2store(fh):
    data = sierra_export_reader(fh)
    with session_scope() as session:
        for element in data:
            bib = BibData(
                sid=prep_ids(element.bid),
                author=element.author,
                title=find_nth_value(element.title, -1),
                pub_info=find_nth_value(element.pub_info, 0),
                subject=find_nth_value(element.subject, 0),
                call_no=find_nth_value(element.call_no, 0),
                mat_cat_id=REBALANCE_CATS[
                    determine_mat_category(element.call_no)][0],
                audn_id=determine_audience_id(element.location),
                lang_id=LANG_CODES[determine_language(element.call_no)][0]
            )

            item = ItemData(
                sid=prep_ids(element.iid),
                bib_id=prep_ids(element.bid),
                # shelf_id=determine_shelf_id(element.location),
                status_id=determine_status_id(element.status),
                item_type_id=determine_item_type_id(
                    session, element.item_type),
                checkouts=int(element.checkouts),
                last_checkout=normalize_date(element.last_checkout))

            insert_or_update(
                session,
                Bib,
                **bib._asdict())

            insert_or_update(
                session,
                Item,
                **item._asdict())

            insert(
                session,
                Hold,
                item_id=item.sid,
                src_branch_id=determine_branch_id(element.location))
