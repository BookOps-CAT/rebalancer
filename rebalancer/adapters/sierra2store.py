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


from datastore import (session_scope, Audience, Branch, Language,
                       ItemType, OverflowItem, MatCat,
                       ShelfCode)
from datastore_transactions import create_code_idx, insert, retrieve_record

RowData = namedtuple(
    'RowData',
    'bib_id, bib_created_date, title, author, pub_info, call_no,'
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

BPL_CALL_PATTERNS = OrderedDict(
    fi=re.compile(r'.*FIC\s', re.IGNORECASE),
    pi=re.compile(r'.*\sJ-E\s|.*J-E$|^J-E.*', re.IGNORECASE),
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
    bi=re.compile(r'^B\s.*|\sB\s.*', re.IGNORECASE)
)


BPL_OPAC_MSGS = {
    'l': 'lp',
    'n': 'rm',
    'y': 'st',
    'k': 'yr',
    'e': 'er',
    'u': 'gn',
    'm': 'my',
    't': 'hi',
    's': 'sf'
}


def prep_ids(sierra_id):
    try:
        return int(sierra_id[1:-1])
    except TypeError:
        return
    except ValueError:
        return


def prep_title(title):
    title = title.strip()
    if '880-' == title[:4]:
        title = title[7:]
    if ' / ' in title:
        parts = title.split(' / ')
        title = ' '.join(parts[:-1])
    title = title[:200]  # datastore limit
    return title


def prep_author(author):
    roles = [
        'author',
        'artist',
        'illustrator'
    ]
    author = author.strip()
    if '880-' in author[:4]:
        author = author[7:]
    for role in roles:
        author = author.replace(role, '').strip()
    try:
        while author[-1] in (',', '.'):
            author = author[:-1].strip()
    except IndexError:
        return None
    author = author[:150]  # datastore limit
    return author


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


def parse_shelfcode(location):
    try:
        shelfcode = location[3:].strip()
        if not shelfcode:
            shelfcode = None
    except TypeError:
        shelfcode = None
    return shelfcode


def determine_bpl_mat_cat(call_no, location, opac_msg):
    mat_cat = None
    shelfcode = parse_shelfcode(location)

    try:
        mat_cat = BPL_OPAC_MSGS[opac_msg]
    except KeyError:
        pass

    if mat_cat is None and shelfcode:
        if shelfcode in ('fc', 'pb'):
            # general fiction
            mat_cat = 'fi'
        elif shelfcode == 'sf':
            # science fiction
            mat_cat = 'sf'
        elif shelfcode == 'my':
            # mystery
            mat_cat = 'my'
        elif shelfcode == 'lp':
            # large print
            mat_cat = 'lp'
        elif shelfcode == 'je':
            # picture books
            mat_cat = 'pi'
        elif shelfcode == 'er':
            # easy reader
            mat_cat = 'er'
        elif shelfcode == 'bi':
            # biography
            mat_cat = 'bi'
        elif shelfcode == 'dv':
            # dvd
            mat_cat = 'dv'
        elif shelfcode == 'cd':
            # cds
            mat_cat = 'cd'

    if mat_cat is None:
        for p, v in BPL_CALL_PATTERNS.items():
            m = v.search(call_no)
            if m:
                mat_cat = p
                break
    return mat_cat


def determine_nyp_mat_cat(call_no):
    for p, v in NYP_CALL_PATTERNS.items():
        m = v.search(call_no)
        if m:
            return p


def get_mat_cat_id(call_no, location, opac_msg, system_id, mat_cat_idx):
    if system_id == 1:
        # BPL
        mat_cat = determine_bpl_mat_cat(
            call_no, location, opac_msg)
        mat_cat_id = mat_cat_idx[mat_cat]
    elif system_id == 2:
        # NYPL
        mat_cat = determine_nyp_mat_cat(call_no)
        mat_cat_id = mat_cat_idx[mat_cat]

    return mat_cat_id


def get_audience_id(location, audn_idx):
    try:
        audn = location[2].strip()
    except IndexError:
        return audn_idx[None]
    try:
        return audn_idx[audn]
    except KeyError:
        return audn_idx[None]


def get_language_id(call_no, lang_idx):
    found = False
    for code in lang_idx.keys():
        if code in call_no.replace('-', ' ').lower().split(' '):
            found = True
            return lang_idx[code]
    if not found:
        return lang_idx['eng']


def get_itemtype_id(item_type, itemtype_idx):
    try:
        return itemtype_idx[int(item_type)]
    except KeyError:
        return itemtype_idx[0]


def string2int(amount):
    try:
        return int(amount)
    except ValueError:
        return 0


def get_shelfcode_id(session, location, system_id):
    shelfcode = parse_shelfcode(location)

    shelfcode_record = retrieve_record(
        session, ShelfCode, system_id=system_id, code=shelfcode)

    # add code if not found
    if shelfcode_record is None:
        shelfcode_record = insert(
            session,
            ShelfCode,
            system_id=system_id,
            code=shelfcode)
        session.flush()

    return shelfcode_record.rid


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
        mat_cat_idx = create_code_idx(session, MatCat, system_id=system_id)
        audn_idx = create_code_idx(session, Audience)
        lang_idx = create_code_idx(session, Language)
        itemtype_idx = create_code_idx(session, ItemType, system_id=system_id)

        for element in data:
            # parse source shelf code and store it
            shelfcode_id = get_shelfcode_id(
                session, element.location, system_id)

            overflow_item = dict(
                system_id=system_id,
                bib_id=prep_ids(element.bib_id),
                title=prep_title(element.title),
                author=prep_author(element.author),
                call_no=element.call_no.strip(),
                item_id=prep_ids(element.item_id),
                src_branch_id=determine_branch_id(
                    element.location, branch_idx),
                src_branch_shelf_id=shelfcode_id,
                pub_date=parse_pub_date(element.pub_info),
                bib_created_date=string2date(element.bib_created_date),
                item_created_date=string2date(element.item_created_date),
                mat_cat_id=get_mat_cat_id(
                    element.call_no, element.location, element.opac_msg,
                    system_id, mat_cat_idx),
                audn_id=get_audience_id(element.location, audn_idx),
                lang_id=get_language_id(element.call_no, lang_idx),
                item_type_id=get_itemtype_id(
                    element.item_type, itemtype_idx),
                last_out_date=string2date(element.last_out_date),
                total_checkouts=string2int(element.total_checkouts),
                total_renewals=string2int(element.total_renewals))

            insert(session, OverflowItem, **overflow_item)
