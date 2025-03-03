from sqlalchemy import Column, String, Integer, DateTime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Asset(db.Model):
    __tablename__ = 'assets'

    id = Column(String, primary_key=True)
    asset_type = Column(String, nullable=False)
    asset_status = Column(String, nullable=False)
    db.UniqueConstraint('id', name='asset_id')


class Staff(db.Model):
    __tablename__ = 'staffs'

    id = Column(String, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    division = Column(String, nullable=False)
    department = Column(String, nullable=False)
    title = Column(String, nullable=False)


class Checkout(db.Model):
    __tablename__ = 'checkouts'

    assetid = Column(String, nullable=False, primary_key=True)
    staffid = Column(String, nullable=False)
    department = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    db.UniqueConstraint('assetid', name='check_a_id')


class History(db.Model):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    assetid = Column(String, nullable=False)
    staffid = Column(String, nullable=False)
    department = Column(String, nullable=False)
    division = Column(String, nullable=False)
    checkouttime = Column(DateTime, nullable=False)
    returntime = Column(DateTime, nullable=False)


class GlobalSet(db.Model):
    __tablename__ = 'globalset'

    settingid = Column(String, primary_key=True)
    setting = Column(String, nullable=False)
    db.UniqueConstraint('settingid', name='setting_id')
