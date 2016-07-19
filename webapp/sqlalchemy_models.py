from webapp import config
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime

#  SQLAlchemy Stuff
sql_engine = create_engine(config.SQL_ALCHEMY_DB_URL, echo=True)
SQLAlchemyDeclarativeBase = declarative_base()

##################################################################
###  A base class for fields that are common across all tables ###
##################################################################
class FintechModelBaseMixin:
    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()

    # __table_args__ = {'mysql_engine': 'InnoDB'}
    # __mapper_args__= {'always_refresh': True}

    is_enabled = Column(Boolean, default=True)

    @declared_attr
    def created_by_id(cls):
        return Column("created_by_id", Integer, ForeignKey("users.id"), nullable=True)

    created_on = Column(DateTime)

    @declared_attr
    def modified_by_id(cls):
        return Column("modified_by_id", Integer, ForeignKey("users.id"), nullable=True)

    modified_on = Column(DateTime, nullable=True)

###############################
###  User Table             ###
###############################
class User(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    type = Column(Integer, default=1) # 1 = PP, 2 = CP, 3 = CP Admin, 4 = Developer

###############################
###  Event Categories Table ###
###############################
class EventCategory(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String)
    name_ar = Column(String)
    is_subcategory = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey(id), nullable=True)
    # create a 2 way self referencing relationship (need to understand this more)
    children = relationship("EventCategory", backref=backref('parent', remote_side=[id]))

###############################
###  Events Table           ###
###############################
class Event(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String)
    name_ar = Column(String)
    type = Column(Integer, default=1) # 1 = single day event, 2 = range date event
    starts_on = Column(Date)
    ends_on = Column(Date, nullable=True)
    company_id = Column(Integer, nullable=True)

###############################
###  Countries Table        ###
###############################
class Country(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String, unique=True)
    name_ar = Column(String, unique=True)

###############################
###  Markets Table          ###
###############################
class Market(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String, unique=True)
    name_ar = Column(String, unique=True)
    symbol = Column(String)
    # FK to country
    country_id = Column(Integer, ForeignKey(Country.id))
    country = relationship(Country, backref="markets")

###############################
###  Sectors Table          ###
###############################
class Sector(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String)
    name_ar = Column(String)

###############################
###  Companies Table        ###
###############################
class Company(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    full_name_en = Column(String)
    full_name_ar = Column(String)
    short_name_en = Column(String)
    short_name_ar = Column(String)
    stock_symbol = Column(String)
    logo_url = Column(String)
    # FK to market
    market_id = Column(Integer, ForeignKey(Market.id))
    market = relationship(Market, backref="companies")

###############################
###  Commodities Table      ###
###############################
class Commodity(FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String)
    name_ar = Column(String)

###############################
###  Stock Prices Table     ###
###############################
class StockPrice(SQLAlchemyDeclarativeBase):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_entity_type_id = Column(Integer) # 1 = company, 2 = commodity, 3 = market, 4 = sector, 5 = ...
    stock_entity_id = Column(Integer)
    for_date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    open = Column(Numeric)
    close = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    volume = Column(Numeric)
    amount = Column(Numeric)
    change = Column(Numeric)
    change_percent = Column(Numeric)

SQLAlchemyDeclarativeBase.metadata.create_all(sql_engine)

a = 1
