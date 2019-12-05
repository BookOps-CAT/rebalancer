"""
Defines and initiates database
"""
from contextlib import contextmanager
from datetime import datetime
import sqlite3

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


from data.branches import BRANCH_CODES
from data.audiences import AUDN_CODES
from data.languages import LANG_CODES
from data.categories import REBALANCE_CATS
from data.status import STATUS_CODES
from datastore_transactions import insert


Base = declarative_base()

DB_FH = './temp/store.db'


class Cart(Base):
    __tablename__ = 'cart'
    sid = Column(Integer, primary_key=True)
    google_sheet_id = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.now())

    def __repr(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Cart({attrs})>'


class Audience(Base):
    __tablename__ = 'audience'
    sid = Column(Integer, primary_key=True, autoincrement=False)
    code = Column(String(1), unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Audience({attrs})>'


class Branch(Base):
    __tablename__ = 'branch'
    sid = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True)
    label = Column(String(100))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Branch({attrs})>'


class Language(Base):
    __tablename__ = 'language'
    sid = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Language({attrs})>'


class Shelf(Base):
    __tablename__ = 'shelf'
    sid = Column(Integer, primary_key=True)
    code = Column(String(5), unique=True)
    label = Column(String(50))
    linear_feet = Column(Float)
    est_items = Column(Integer)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Shelf({attrs})>'


class Status(Base):
    __tablename__ = 'status'
    sid = Column(Integer, primary_key=True)
    code = Column(String(1), unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Status({attrs})>'


class ItemType(Base):
    __tablename__ = 'item_type'
    sid = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True)
    label = Column(String(75))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<ItemType({attrs})>'


class MatCat(Base):
    __tablename__ = 'mat_cat'
    sid = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True)
    label = Column(String(100), nullable=False)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<MatCat({attrs})>'


class Bib(Base):
    __tablename__ = 'bib'
    sid = Column(Integer, primary_key=True, autoincrement=False)
    mat_cat_id = Column(Integer, ForeignKey('mat_cat.sid'), nullable=False)
    audn_id = Column(
        Integer, ForeignKey('audience.sid'), nullable=False)
    lang_id = Column(
        Integer, ForeignKey('language.sid'), nullable=False)
    author = Column(String(100))
    title = Column(String(150), nullable=False)
    pub_info = Column(String(150))
    call_no = Column(String(150))
    subject = Column(String(500))
    rating = Column(Float)

    items = relationship(
        'Item',
        lazy='joined',
        cascade='all, delete-orphan')

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Bib({attrs})>'


class Item(Base):
    __tablename__ = 'item'
    sid = Column(Integer, primary_key=True, autoincrement=False)
    bib_id = Column(Integer, ForeignKey('bib.sid'), nullable=False)
    status_id = Column(Integer, ForeignKey('status.sid'), nullable=False)
    item_type_id = Column(Integer, ForeignKey('item_type.sid'), nullable=False)
    barcode = Column(String(14))
    checkouts = Column(Integer, default=0)
    last_checkout = Column(DateTime)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Item({attrs})>'


class Hold(Base):
    __tablename__ = 'hold'
    sid = Column(Integer, primary_key=True)
    hid = Column(Integer)
    cart_id = Column(Integer, ForeignKey('cart.sid'))
    item_id = Column(Integer, ForeignKey('item.sid'), nullable=False)
    src_branch_id = Column(Integer, ForeignKey('branch.sid'), nullable=False)
    dst_branch_id = Column(Integer, ForeignKey('branch.sid'))
    timestamp = Column(DateTime, nullable=False, default=datetime.now())
    outstanding = Column(Boolean, nullable=False, default=True)
    issued = Column(Boolean, nullable=False, default=False)
    fulfilled = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Hold({attrs})>'


class DataAccessLayer:

    def __init__(self):
        self.db_path = f'sqlite:///{DB_FH}'
        self.engine = None
        self.Session = None

    def connect(self):
        self.engine = create_engine(self.db_path)
        self.Session = sessionmaker(bind=self.engine)


dal = DataAccessLayer()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    dal.connect()
    session = dal.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_datastore():
    conn = sqlite3.connect(DB_FH)
    conn.close()
    engine = create_engine(f'sqlite:///{DB_FH}')
    Base.metadata.create_all(engine)

    with session_scope() as session:
        for code, values in AUDN_CODES.items():
            insert(
                session, Audience, sid=values[0], code=code, label=values[1])

        for code, values in LANG_CODES.items():
            insert(
                session,
                Language,
                sid=values[0], code=code, label=values[1])

        for code, values in BRANCH_CODES.items():
            insert(
                session,
                Branch,
                sid=values[0], code=code, label=values[1])

        for code, values in REBALANCE_CATS.items():
            insert(
                session,
                MatCat,
                sid=values[0], code=code, label=values[1])

        for code, values in STATUS_CODES.items():
            insert(
                session,
                Status,
                sid=values[0], code=code, label=values[1])


if __name__ == '__main__':
    create_datastore()
