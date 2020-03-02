"""
Defines and initiates database
"""
from contextlib import contextmanager
from datetime import datetime
import json
import sqlite3

from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, String, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


from datastore_transactions import insert


Base = declarative_base()

DB_FH = './temp/store.db'


class System(Base):
    __tablename__ = 'system'
    rid = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True)
    label = Column(String(25))

    def __repr__(self):
        return f"<System(rid='{self.rid}', code='{self.code}', " \
               f"label='{self.name}')>"


class Cart(Base):
    __tablename__ = 'cart'
    rid = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    shopping_cart_id = Column(String, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.now())

    items = relationship(
        'OverflowItem',
        cascade='all, delete-orphan',
        lazy='joined')

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Cart({attrs})>'


class Audience(Base):
    __tablename__ = 'audience'
    rid = Column(Integer, primary_key=True)
    code = Column(String(1), unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Audience({attrs})>'


class Branch(Base):
    __tablename__ = 'branch'
    __table_args__ = (
        UniqueConstraint('system_id', 'code', name='uix_branch'), )
    rid = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    active = Column(Boolean, default=True)
    code = Column(String(2))
    label = Column(String(100))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Branch({attrs})>'


class ShelfCode(Base):
    __tablename__ = 'shelf_code'
    __table_args__ = (
        UniqueConstraint('code', 'system_id', name='uix_shelfcodes'), )
    rid = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    code = Column(String(3))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<ShelfCode({attrs})>'


class Language(Base):
    __tablename__ = 'language'
    rid = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Language({attrs})>'


class ItemType(Base):
    __tablename__ = 'item_type'
    __table_args__ = (
        UniqueConstraint('code', 'system_id', name='uix_itemtype'), )
    rid = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    code = Column(String(3), unique=True)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<ItemType({attrs})>'


class MatCat(Base):
    __tablename__ = 'mat_cat'
    __table_args__ = (
        UniqueConstraint('code', 'system_id', name='uix_matcat'), )
    rid = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    code = Column(String(2))
    label = Column(String(100), nullable=False)
    adult_order = Column(Integer)
    teen_order = Column(Integer)
    kids_order = Column(Integer)
    wl_order = Column(Integer)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<MatCat({attrs})>'


class OverflowItem(Base):
    __tablename__ = 'overflow_item'
    rid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now())
    system_id = Column(Integer, ForeignKey('system.rid'), nullable=False)
    cart_id = Column(Integer, ForeignKey('cart.rid'))
    bib_id = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)
    src_branch_id = Column(Integer, ForeignKey('branch.rid'), nullable=False)
    src_branch_shelf_id = Column(
        Integer, ForeignKey('shelf_code.rid'), nullable=False)
    dst_branch_id = Column(Integer, ForeignKey('branch.rid'), nullable=False)
    pub_date = Column(String(4))
    bib_created_date = Column(Date)
    item_created_date = Column(Date)
    mat_cat_id = Column(Integer, ForeignKey('mat_cat.rid'), nullable=False)
    audn_id = Column(Integer, ForeignKey('audience.rid'), nullable=False)
    lang_id = Column(Integer, ForeignKey('language.rid'), nullable=False)
    item_type_id = Column(Integer, ForeignKey('item_type.rid'), nullable=False)
    last_out_date = Column(String(20), default=None)
    total_checkouts = Column(Integer, default=0)
    total_renewals = Column(Integer, default=0)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Stats({attrs})>'


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

        systems = [
            {
                'rid': 1,
                'code': 'BKL',
                'label': 'Brooklyn Public Library'
            },
            {
                'rid': 2,
                'code': 'NYP',
                'label': 'New York Public Library'}]

        for value in systems:
            insert(
                session, System, **value)

        with open('./data/audiences.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            for value in data:
                insert(
                    session, Audience, **value)

        with open('./data/branches.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            for value in data:
                insert(
                    session, Branch, **value)

        with open('./data/categories.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            for value in data:
                insert(
                    session, MatCat, **value)

        with open('./data/languages.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            for value in data:
                insert(
                    session, Language, **value)


if __name__ == '__main__':
    create_datastore()
