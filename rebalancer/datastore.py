"""
Defines and initiates database
"""
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
# from sqlalchemy.orm import relationship, sessionmaker
# from sqlalchemy import create_engine
# from sqlalchemy.engine.url import URL


Base = declarative_base()

# DB_DIALECT = 'sqlite'
# DB_DRIVER = 'pysqlite'
# DB_CHARSET = 'utf8'
# TIMEOUT = 10


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


class MatCat(Base):
    __tablename__ = 'matcat'
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
    matcat_id = Column(Integer, ForeignKey('matcat.sid'), nullable=False)
    author = Column(String(100))
    title = Column(String(150), nullable=False)
    rating = Column(Float)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<Bib({attrs})>'


class Item(Base):
    __tablename__ = 'item'
    sid = Column(Integer, primary_key=True, autoincrement=False)
    bib_id = Column(Integer, ForeignKey('bib.sid'), nullable=False)
    barcode = Column(String(14))
    circ = Column(Integer, default=0)
    last_circ = Column(DateTime)

    def __repr__(self):
        state = inspect(self)
        attrs = ', '.join([
            f'{attr.key}={attr.loaded_value!r}' for attr in state.attrs])
        return f'<item({attrs})>'


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
        return f'<item({attrs})>'
