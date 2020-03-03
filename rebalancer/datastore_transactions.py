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



# def insert_or_ignore(session, model, **kwargs):
#     instance = session.query(model).filter_by(**kwargs).first()
#     if not instance:
#         instance = model(**kwargs)
#         session.add(instance)
#     return instance


# def delete_record(session, model, **kwargs):
#     instance = session.query(model).filter_by(**kwargs).one()
#     session.delete(instance)


# def update_record(session, model, rid, **kwargs):
#     instance = session.query(model).filter_by(rid=rid).one()
#     for key, value in kwargs.items():
#         setattr(instance, key, value)


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


# def get_items4cart(session, audn_id, mat_cat_id, lang_id):
#     # refactor for eng only
#     if lang_id == 5:
#         # 'eng' lang id
#         lang_operator = '='
#     else:
#         # world lang ids
#         lang_operator = '<>'

#     stmn = f"""
#         SELECT item.sid as iid,
#                bib.sid as bid,
#                branch.code as branch,
#                status.code as status,
#                item_type.code as item_type,
#                mat_cat.code as mat_cat,
#                audience.code as audn,
#                language.code as lang,
#                bib.author as author,
#                bib.title as title,
#                bib.pub_info as pub_info,
#                bib.call_no as call_no,
#                bib.subject as subject,
#                hold.sid as hold_id
#         FROM item
#         JOIN bib ON item.bib_id = bib.sid
#         JOIN hold ON item.sid = hold.item_id
#         JOIN branch ON hold.src_branch_id = branch.sid
#         JOIN status ON item.status_id = status.sid
#         JOIN item_type ON item.item_type_id = item_type.sid
#         JOIN mat_cat ON bib.mat_cat_id = mat_cat.sid
#         JOIN audience ON bib.audn_id = audience.sid
#         JOIN language ON bib.lang_id = language.sid
#             WHERE hold.outstanding=:outstanding
#                   AND mat_cat.sid=:mat_cat_id
#                   AND audience.sid=:audn_id
#                   AND language.sid{lang_operator}:lang_id
#             ORDER BY bib.call_no, bib.author, bib.title;
#     """

#     stmn = text(stmn)
#     stmn = stmn.bindparams(
#         outstanding=True, mat_cat_id=mat_cat_id,
#         audn_id=audn_id, lang_id=lang_id)
#     instances = session.execute(stmn)
#     return instances
