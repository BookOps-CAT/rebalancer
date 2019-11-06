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


Base = declarative_base()

DB_FH = './temp/store.db'


class Branch(Base):
    __tablename__ = 'branch'
    sid = Column(Integer, primary_key=True)
    code = Column(String(2), nullable=False, unique=True)
    label = Column(String(100))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Branch({attrs})>'


class Shelf(Base):
    __tablename__ = 'shelf'
    sid = Column(Integer, primary_key=True)
    code = Column(String(5), nullable=False, unique=True)
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
    code = Column(String(1), nullable=False, unique=True)
    label = Column(String(50))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Status({attrs})>'


class ItemType(Base):
    __tablename__ = 'item_type'
    sid = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False, unique=True)
    label = Column(String(75))

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<ItemType({attrs})>'


class MatCat(Base):
    __tablename__ = 'mat_cat'
    sid = Column(Integer, primary_key=True)
    code = Column(String(2), nullable=False, unique=True)
    label = Column(String(100), nullable=False)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<MatCat({attrs})>'


class Bib(Base):
    __tablename__ = 'bib'
    sid = Column(Integer, primary_key=True, autoincrement=False)
    matcat_id = Column(Integer, ForeignKey('mat_cat.sid'), nullable=False)
    author = Column(String(100))
    title = Column(String(150), nullable=False)
    pub_info = Column(String(150))
    call_no = Column(String(150))
    subjects = Column(String(500))
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
    branch_id = Column(Integer, ForeignKey('branch.sid'), nullable=False)
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
    hid = Column(Integer, unique=True)
    item_id = Column(Integer, ForeignKey('item.sid'), nullable=False)
    src_branch_id = Column(Integer, ForeignKey('branch.sid'), nullable=False)
    dst_branch_id = Column(Integer, ForeignKey('branch.sid'), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now())
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


if __name__ == '__main__':
    create_datastore()
