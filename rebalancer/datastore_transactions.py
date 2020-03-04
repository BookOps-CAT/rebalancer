"""
Datastore transaction methods
"""

from functools import lru_cache

from sqlalchemy.sql import text
# from pandas import read_sql


from errors import RebalancerError


def retrieve_records(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).order_by(
        model.rid).all()
    return instances


def insert(session, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    return instance


def create_code_idx(session, model, **kwargs):
    records = retrieve_records(
        session, model, **kwargs)
    branch_idx = {x.code: x.rid for x in records}

    return branch_idx


def retrieve_record(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    return instance


@lru_cache(maxsize=32)
def retrieve_record_cached(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    return instance


def update_record(session, model, rid, **kwargs):
    instance = session.query(model).filter_by(rid=rid).one()
    for key, value in kwargs.items():
        setattr(instance, key, value)


# def insert_or_ignore(session, model, **kwargs):
#     instance = session.query(model).filter_by(**kwargs).first()
#     if not instance:
#         instance = model(**kwargs)
#         session.add(instance)
#     return instance


# def delete_record(session, model, **kwargs):
#     instance = session.query(model).filter_by(**kwargs).one()
#     session.delete(instance)


# def insert_or_update(session, model, rid, **kwargs):
#     instance = session.query(model).filter_by(rid=rid).first()
#     if not instance:
#         instance = model(**kwargs)
#         session.add(instance)
#     else:
#         del kwargs['sid']
#         update_record(session, model, rid, **kwargs)


# def retrieve_records(session, model, **kwargs):
#     instances = session.query(model).filter_by(**kwargs).order_by(
#         model.rid).all()
#     return instances


# def retrieve_last_record(session, model):
#     instance = session.query(model).order_by(model.rid.desc()).first()
#     return instance


def get_items4cart(session, system_id, audn_id, mat_cat_id, english_lang=True):
    if english_lang:
        # English materials
        lang_operator = '='
    else:
        # world languages
        lang_operator = '<>'

    stmn = f"""
        SELECT overflow_item.rid as rid,
               overflow_item.item_id as iid,
               overflow_item.bib_id as bid,
               overflow_item.title as title,
               overflow_item.author as author,
               overflow_item.call_no as call_no,
               overflow_item.pub_date as pub_date,
               branch.code as branch,
               mat_cat.code as mat_cat,
               audience.code as audn,
               language.code as lang
        FROM overflow_item
        JOIN branch ON overflow_item.src_branch_id = branch.rid
        JOIN mat_cat ON overflow_item.mat_cat_id = mat_cat.rid
        JOIN audience ON overflow_item.audn_id = audience.rid
        JOIN language ON overflow_item.lang_id = language.rid
            WHERE overflow_item.cart_id IS NULL
                AND overflow_item.system_id=:system_id
                AND mat_cat.rid=:mat_cat_id
                AND audience.rid=:audn_id
                AND language.code{lang_operator}'eng'
            ORDER BY call_no, author, title;
    """

    stmn = text(stmn)
    stmn = stmn.bindparams(
        system_id=system_id,
        mat_cat_id=mat_cat_id,
        audn_id=audn_id)
    instances = session.execute(stmn)
    return instances
