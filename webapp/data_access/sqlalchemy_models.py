from webapp.app import db, config
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime

#  SQLAlchemy Stuff
# sql_engine = create_engine(config.SQL_ALCHEMY_DB_URL, echo=False)
# DbSession = sessionmaker(bind=sql_engine)
# SQLAlchemyDeclarativeBase = declarative_base()

##################################
### Column Default Value Funcs ###
##################################
def short_name_en_default(context):
    try:
        return context.current_parameters.get('name_en')
    except:
        return None

def short_name_ar_default(context):
    try:
        return context.current_parameters.get('name_ar')
    except:
        return None

##################################################################
###  Base classes for fields that are common across all tables ###
##################################################################
class CommonModelBaseMixin:
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

class StockModelBaseMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)
    argaam_id = Column(Integer, nullable=True)
    name_en = Column(String)
    name_ar = Column(String)
    short_name_en = Column(String, default=short_name_en_default)
    short_name_ar = Column(String, default=short_name_ar_default)

###############################
###  User Table             ###
###############################
class User(UserMixin, CommonModelBaseMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    type = Column(Integer, default=1) # 1 = PP, 2 = CP, 3 = CP Admin, 4 = Developer

###############################
###  Countries Table        ###
###############################
class Country(CommonModelBaseMixin, StockModelBaseMixin, db.Model):
    __tablename__ = "countries"

    def __str__(self):
        return self.name_en
###############################
###  Markets Table          ###
###############################
class Market(CommonModelBaseMixin, StockModelBaseMixin, db.Model):
    __tablename__ = "markets"

    symbol = Column(String)
    # FK to country
    country_id = Column(Integer, ForeignKey(Country.id), nullable=True)
    country = relationship(Country, backref="markets")
   
    def __str__(self):
        return self.short_name_en
###############################
###  Sectors Table          ###
###############################
class Sector(CommonModelBaseMixin, StockModelBaseMixin, db.Model):
    __tablename__ = "sectors"

###############################
###  Companies Table        ###
###############################
class Company(CommonModelBaseMixin, StockModelBaseMixin, db.Model):
    __tablename__ = "companies"

    stock_symbol = Column(String)
    logo_url = Column(String)
    # FK to market
    market_id = Column(Integer, ForeignKey(Market.id))
    market = relationship(Market, backref="companies")

    def __str__(self):
        return self.short_name_en
###############################
###  Commodities Table      ###
###############################
class Commodity(CommonModelBaseMixin, StockModelBaseMixin, db.Model):
    __tablename__ = "commodities"

###############################
###  Stock Prices Table     ###
###############################
class StockPrice(db.Model):
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


###############################
###  Event Categories Table ###
###############################
class EventCategory(CommonModelBaseMixin, db.Model):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String)
    name_ar = Column(String)
    is_subcategory = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey(id), nullable=True)
    # create a 2 way self referencing relationship (need to understand this more)
    parent = relationship("EventCategory", remote_side=[id], backref = 'children') #, primaryjoin='EventCategory.is_subcategory==False')

    def __str__(self):
        return self.name_en

###############################
###  Event Groups Table ###
###############################
class EventGroup(CommonModelBaseMixin, db.Model):
    __tablename__ = "event_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String)
    name_ar = Column(String)

    def __str__(self):
        return self.name_en

###############################
###  Events Table           ###
###############################
class Event(CommonModelBaseMixin, db.Model):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String)
    name_ar = Column(String)
    type = Column(Integer, default=1) # 1 = single day event, 2 = range date event
    starts_on = Column(Date)
    ends_on = Column(Date, nullable=True)
    # company_id = Column(Integer, nullable=True)
    company_id = Column(Integer, ForeignKey(Company.id))
    company = relationship(Company, backref="events")
    event_category_id = Column(Integer, ForeignKey(EventCategory.id))
    event_category = relationship(EventCategory, backref="events")
    event_group_id = Column(Integer, ForeignKey(EventGroup.id), nullable=False)
    event_group = relationship(EventGroup, backref="events")
    
    def __str__(self):
        return self.name_en

######################################
### Just some sample rows and code ###
######################################
def create_sample_sp_rows():
    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 5
    sp.for_date = datetime(2001, 1, 1)
    sp.year = 2001
    sp.month = 1
    sp.open = 100.01
    sp.close = 101.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.33

    db.session.add(sp)

    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 5
    sp.for_date = datetime(2002, 2, 2)
    sp.year = 2002
    sp.month = 2
    sp.open = 123.01
    sp.close = 144.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.99

    db.session.add(sp)

    sp = StockPrice()
    sp.stock_entity_type_id = 2
    sp.stock_entity_id = 7
    sp.for_date = datetime(2012, 2, 2)
    sp.year = 2012
    sp.month = 2
    sp.open = 123.01
    sp.close = 144.11
    sp.min = sp.max = sp.volume = sp.amount = sp.change = sp.change_percent = 33.99

    db.session.add(sp)

    db.session.commit()
    db.session.close()

# session = DbSession()
# result = session.query(STOCK_ENTITY_TYPE_TABLE_NAME[2]).select_from().filter("id = %s" % 4).first()
# print(result)

# print(STOCK_ENTITY_TYPE_TABLE_NAME[1])

###############################
###  CREATE THE TABLES      ###
###############################
# SQLAlchemyDeclarativeBase.metadata.create_all(sql_engine)
db.create_all()

########################################
### Create 1st User if doesn't exist ###
########################################
# sql_engine = create_engine(config.SQL_ALCHEMY_DB_URL, echo=False)
# DbSession = sessionmaker(bind=sql_engine)
# session = DbSession()
#
# for u in session.query(User).all():
#     print(u.email)

if db.session.query(User.id).filter(User.email == 'fintechadmin@danatev.com').scalar() is None:
    user = User()
    user.email = 'fintechadmin@danatev.com'
    user.password = 'ftAdmin123$$$'
    user.type = 3
    db.session.add(user)
    db.session.commit()
    db.session.close()
