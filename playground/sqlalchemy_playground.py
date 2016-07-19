from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from webapp import config
import datetime

# print(sqlalchemy.__version__)

#engine = create_engine(config.SQL_ALCHEMY_DB_URL)

memory_engine = create_engine("sqlite:///d:/test.db", echo=True)
Base = declarative_base()
MemDbSession = sessionmaker(memory_engine)

def create_and_select_from_table():
    engine = create_engine("sqlite://", echo=True)
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True)
        full_name = Column(String)
        email_address = Column(String)
        amount = Column(Numeric(2, 10))

    Base.metadata.create_all(engine)

def print_all_event_categories():
    engine = create_engine(config.SQL_ALCHEMY_DB_URL, echo=False)

    # Base = automap_base()
    # Base.prepare(engine, reflect=True)
    # EventCategory = Base.classes.EventCategories

    Base = declarative_base()
    class EventCategory(Base):
        __tablename__ = "EventCategories"
        EventCategoryID = Column("EventCategoryID", Integer, primary_key=True, autoincrement=True)
        Name = Column("EventCategoryName", String)
        IsSubCategory = Column("IsSubcategory", Boolean)
        ParentCategoryID = Column(Integer, default=0)

    db_session = sessionmaker(engine)
    session = db_session()

    # ec1 = EventCategory(Name='Added By SQLAlchemy', IsSubCategory=False)
    #
    # session.add(ec1)

    # for ec in session.query(EventCategory).order_by(EventCategory.Name):
    #     print(ec.EventCategoryID, ec.Name, ec.IsSubCategory, ec.ParentCategoryID)

    noi = session.query(EventCategory).count()

    print(noi)

    session.commit()
    session.close()

def play_with_declarative():
    engine = create_engine("sqlite://", echo=True)
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    u = User()

    print(User.__table__)

def understand_relationships():
    class Department(Base):
        __tablename__ = "departments"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, unique=True)

        employees = relationship("Employee", back_populates="department") #backref="Department")

    class Employee(Base):
        __tablename__ = "employees"

        id = Column(Integer, primary_key=True, autoincrement=True)
        full_name = Column(String)
        email = Column(String, unique=True)
        dob = Column(Date)
        # reference to the department the employee belongs to
        department_id = Column(Integer, ForeignKey("departments.id"))
        # create the relationship (this is only to be used at python level, has nothing to do with the DB :)
        department = relationship(Department, back_populates="employees") # backref="employees")

    sales = Department(name="Sales")
    emp1 = Employee(full_name="Adnan Hussain", email="adnanshussain@gmail.com", dob=datetime.date(1976, 8, 18), department=sales)
    emp2 = Employee(full_name="Akbar Khan", email="akbarkhan@gmail.com", dob=datetime.date(1980, 3, 3), department=sales)
    emp3 = Employee(full_name="Hunaid Mushtaq", email="hm@gmail.com", dob=datetime.date(1977, 1, 20), department=sales)

    for e in sales.employees:
        print(e.department)

    #
    # Base.metadata.create_all(memory_engine)
    #
    # session = MemDbSession()
    # session.add_all([sales, emp1, emp2, emp3])

    # sales = session.query(Department).first()
    # for e in sales.employees:
    #     print(e.full_name)

    # session.commit()
    # session.close()

# print(type(MemDbSession))

understand_relationships()
