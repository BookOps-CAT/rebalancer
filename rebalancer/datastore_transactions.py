"""
Datastore transaction methods
"""

from functools import lru_cache

from sqlalchemy.sql import text, case
# from pandas import read_sql


from errors import RebalancerError


def count_records(session, model, **kwargs):
    record_count = session.query(model).filter_by(**kwargs).count()
    return record_count


def retrieve_records(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).order_by(
        model.rid).all()
    return instances


def retrieve_records_ordered_by_code(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).order_by(
        model.code).all()
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

def world_lang_query_stmn(system_id, lang_code):
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
                AND language.code=:lang_code
            ORDER BY call_no, author, title;
    """
    stmn = text(stmn)
    stmn = stmn.bindparams(
        system_id=system_id,
        lang_code=lang_code)
    return stmn


def english_query_stmn(system_id, audn_id, mat_cat_id):
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
                AND language.code='eng'
            ORDER BY call_no, author, title;
    """

    stmn = text(stmn)
    stmn = stmn.bindparams(
        system_id=system_id,
        mat_cat_id=mat_cat_id,
        audn_id=audn_id)
    return stmn


def get_relevant_lang_recs(session, system_id):
    stmn = f"""
        SELECT DISTINCT language.rid, language.code, language.label
          FROM language
            JOIN overflow_item ON language.rid = overflow_item.lang_id
          WHERE overflow_item.system_id=:system_id
            AND overflow_item.cart_id IS NULL
            AND language.code <> 'eng'
          ORDER BY language.code
    """
    stmn = text(stmn)
    stmn = stmn.bindparams(
        system_id=system_id)
    instances = session.execute(stmn)
    lang_recs = [(c.rid, c.code, c.label) for c in instances]
    return lang_recs


def get_items4cart(session, system_id, audn_id, mat_cat_id, lang_code):
    if lang_code == 'eng':
        # English materials
        stmn = english_query_stmn(system_id, audn_id, mat_cat_id)
    else:
        # world languages
        stmn = world_lang_query_stmn(system_id, lang_code)

    instances = session.execute(stmn)
    return instances
