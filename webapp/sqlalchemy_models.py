from enum import Enum
from webapp import config
from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime

#  SQLAlchemy Stuff
sql_engine = create_engine(config.SQL_ALCHEMY_DB_URL, echo=False)
DbSession = sessionmaker(bind=sql_engine)
SQLAlchemyDeclarativeBase = declarative_base()

###############################
### Custom Enums            ###
###############################
class UserTypesEnum(Enum):
    public_portal = 1
    control_panel = 2
    cp_admin = 3
    developer = 4

###############################
### ID to Name Mappings     ###
###############################
STOCK_ENTITY_TYPE_TABLE_NAME = {
    1: "companies",
    2: "commodities",
    3: "markets",
    4: "sectors"
}

##################################
### Column Default Value Funcs ###
##################################
def short_name_en_default(context):
    return context.current_parameters.get('name_en')

def short_name_ar_default(context):
    return context.current_parameters.get('name_ar')

##################################################################
###  Base classes for fields that are common across all tables ###
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

    created_on = Column(DateTime, default=datetime.now())

    @declared_attr
    def modified_by_id(cls):
        return Column("modified_by_id", Integer, ForeignKey("users.id"), nullable=True)

    modified_on = Column(DateTime, nullable=True)

class FintechStockModelBaseMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String)
    name_ar = Column(String)
    short_name_en = Column(String, default=short_name_en_default)
    short_name_ar = Column(String, default=short_name_ar_default)

###############################
###  User Table             ###
###############################
class User(UserMixin, FintechModelBaseMixin, SQLAlchemyDeclarativeBase):
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
    children = relationship("EventCategory", backref=backref('parent', remote_side=[id])) #, primaryjoin='EventCategory.is_subcategory==False')

    def __str__(self):
        return self.name_en

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
class Country(FintechModelBaseMixin, FintechStockModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "countries"

###############################
###  Markets Table          ###
###############################
class Market(FintechModelBaseMixin, FintechStockModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "markets"

    symbol = Column(String)
    # FK to country
    country_id = Column(Integer, ForeignKey(Country.id), nullable=True)
    country = relationship(Country, backref="markets")

###############################
###  Sectors Table          ###
###############################
class Sector(FintechModelBaseMixin, FintechStockModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "sectors"

###############################
###  Companies Table        ###
###############################
class Company(FintechModelBaseMixin, FintechStockModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "companies"

    stock_symbol = Column(String)
    logo_url = Column(String)
    # FK to market
    market_id = Column(Integer, ForeignKey(Market.id))
    market = relationship(Market, backref="companies")

###############################
###  Commodities Table      ###
###############################
class Commodity(FintechModelBaseMixin, FintechStockModelBaseMixin, SQLAlchemyDeclarativeBase):
    __tablename__ = "commodities"

###############################
###  Stock Prices Table     ###
###############################
class StockPrice(SQLAlchemyDeclarativeBase):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_entity_type_id = Column(Integer) # 1 = company, 2 = commodity, 3 = market, 4 = sector, 5 = ...
    stock_entity_id = Column(Integer)
    stock_entity_argaam_id = Column(Integer)
    for_date = Column(Date)
    year = Column(Integer)
    month = Column(Integer)
    open = Column(Numeric)
    close = Column(Numeric)
    min = Column(Numeric)
    max = Column(Numeric)
    volume = Column(Numeric, nullable=True)
    amount = Column(Numeric, nullable=True)
    change = Column(Numeric)
    change_percent = Column(Numeric)

    def __str__(self):
        return "%s %s %s" % (self.id, self.for_date, self.close)

######################################
### Just some sample rows and code ###
######################################
def create_sample_sp_rows():
    session = DbSession()

    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 5
    sp.for_date = datetime(2001, 1, 1)
    sp.year = 2001
    sp.month = 1
    sp.open = 100.01
    sp.close = 101.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.33

    session.add(sp)

    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 5
    sp.for_date = datetime(2002, 2, 2)
    sp.year = 2002
    sp.month = 2
    sp.open = 123.01
    sp.close = 144.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.99

    session.add(sp)

    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 7
    sp.for_date = datetime(2012, 2, 2)
    sp.year = 2012
    sp.month = 2
    sp.open = 123.01
    sp.close = 144.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.99

    session.add(sp)

    session.commit()
    session.close()

# print(STOCK_ENTITY_TYPE_TABLE_NAME[1])

###############################
###  CREATE THE TABLES      ###
###############################
SQLAlchemyDeclarativeBase.metadata.create_all(sql_engine)