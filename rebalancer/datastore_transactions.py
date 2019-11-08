"""
Datastore transaction methods
"""


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


def retrieve_record(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    return instance


def retrieve_records(session, model, **kwargs):
    instances = session.query(model).filter_by(**kwargs).order_by(
        model.sid).all()
    return instances
