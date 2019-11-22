"""
Datastore transaction methods
"""

from functools import lru_cache

from sqlalchemy.sql import text
# from pandas import read_sql


def insert(session, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    session.flush()
    return instance


def insert_or_ignore(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
    return instance


def delete_record(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one()
    session.delete(instance)


def update_record(session, model, sid, **kwargs):
    instance = session.query(model).filter_by(sid=sid).one()
    for key, value in kwargs.items():
        setattr(instance, key, value)


def insert_or_update(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
    else:
        sid = kwargs['sid']
        del kwargs['sid']
        update_record(session, model, sid, **kwargs)


@lru_cache(maxsize=32)
def retrieve_record(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    return instance


def retrieve_records(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).order_by(
        model.sid).all()
    return instances


def get_items4cart(session, audn, mat_cat, lang):
    if lang == 'eng':
        lang_condition = '='
    else:
        lang = 'eng'
        lang_condition = '<>'

    stmn = f"""
        SELECT item.sid as iid,
               bib.sid as bid,
               branch.code as branch,
               status.code as status,
               item_type.code as item_type,
               mat_cat.code as mat_cat,
               audience.code as audn,
               language.code as lang,
               bib.author as author,
               bib.title as title,
               bib.pub_info as pub_info,
               bib.call_no as call_no,
               bib.subject as subject
        FROM item
        JOIN bib ON item.bib_id = bib.sid
        JOIN hold ON item.sid = hold.item_id
        JOIN branch ON hold.src_branch_id = branch.sid
        JOIN status ON item.status_id = status.sid
        JOIN item_type ON item.item_type_id = item_type.sid
        JOIN mat_cat ON bib.mat_cat_id = mat_cat.sid
        JOIN audience ON bib.audn_id = audience.sid
        JOIN language ON bib.lang_id = language.sid
            WHERE hold.issued=:issued
                  AND mat_cat.code=:mat_cat
                  AND audience.code=:audn
                  AND language.code{lang_condition}:lang
            ORDER BY bib.author, bib.title;
    """

    stmn = text(stmn)
    stmn = stmn.bindparams(mat_cat=mat_cat, audn=audn, lang=lang, issued=False)
    instances = session.execute(stmn)
    return instances
