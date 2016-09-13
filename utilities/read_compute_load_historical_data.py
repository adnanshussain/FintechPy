import csv, configparser
from datetime import datetime, date
import pymssql
from sqlalchemy import Table, create_engine, MetaData, Column, Date, Integer, Float
from sqlalchemy.sql.expression import bindparam
from webapp.config import active_config

base_dir = 'HistoricalDataFromTickerCharts'
config_ini = configparser.ConfigParser()

# config_ini['asdf'] = dict(word='adnan', password='abc123$%%')
# with open('example.ini', 'w') as configfile:
#   config_ini.write(configfile)

config_ini.read('../webapp/config.ini')
GULFARGAAM_PROD_SECTION = 'GULFARGAAM PROD'


def _get_mssql_connection(as_dict=False):
    return pymssql.connect(config_ini[GULFARGAAM_PROD_SECTION]['SERVER_IP'],
                           config_ini[GULFARGAAM_PROD_SECTION]['USER_NAME'],
                           config_ini[GULFARGAAM_PROD_SECTION]['PWD'],
                           config_ini[GULFARGAAM_PROD_SECTION]['DB_NAME'],
                           as_dict=as_dict)


def _read_data(file_name):
    with open(base_dir + '\\' + file_name) as csvfile:
        csv_reader = csv.DictReader(csvfile)
        result = [d for d in csv_reader]

    return result


sql = """
    select marketid as market_id, generalindexsymbol as general_symbol_index from market WHERE IsInactive = 0 and IsTradingAvailable = 1;
"""
with _get_mssql_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(sql)
    markets = [record for record in cursor]

###############################
### Configure SQLAlchemy    ###
###############################
engine = create_engine(active_config.SQLALCHEMY_DATABASE_URI)
engine.echo = True

metadata = MetaData()

splits_table = Table('tc_splits', metadata,
                     Column('split_id', Integer, primary_key=True),
                     Column('split_date', Date),
                     Column('company_id', Integer),
                     Column('ratio', Float))

tc_company_stock_prices = Table('tc_company_stock_prices', metadata,
                                Column('id', Integer, primary_key=True, autoincrement=True),
                                Column('market_id', Integer),
                                Column('for_date', Date),
                                Column('company_id', Integer),
                                Column('open', Float),
                                Column('max', Float),
                                Column('min', Float),
                                Column('close', Float),
                                Column('volume', Integer),
                                Column('amount', Integer))

metadata.create_all(bind=engine)


def insert_splits_data():
    stmt_insert_splits = splits_table.insert().values(split_id=bindparam('SplitID'), split_date=bindparam('SplitDate', type_=Date),
                                                      company_id=bindparam('CompanyID'), ratio=bindparam('Ratio;'))
    print(stmt_insert_splits)

    result = _read_data('splits.csv')
    for item in result:
        item['SplitDate'] = datetime.strptime(item['SplitDate'], "%Y-%m-%d").date()
        item['Ratio;'] = float(item['Ratio;'][0:len(item['Ratio;']) - 1])

    # for row in result:
    #     print(row)

    with engine.connect() as conn:
        conn.execute(stmt_insert_splits, result)


def insert_stock_data(country, market_gsi):
    market_id = [ct[0] for ct in markets if ct[1] == market_gsi][0]
    insert_stmt = tc_company_stock_prices.insert().values(for_date=bindparam('DailyDate'),
                                                          market_id=bindparam('market_id'),
                                                          company_id=bindparam('CompanyID'),
                                                          open=bindparam('Open'),
                                                          max=bindparam('Max'),
                                                          min=bindparam('Min'),
                                                          close=bindparam('Close'),
                                                          volume=bindparam('Volume'),
                                                          amount=bindparam('Amount'))
    print(insert_stmt)

    result = _read_data(country + '.csv')

    for item in result:
        item['DailyDate'] = datetime.strptime(item['DailyDate'], "%Y-%m-%d").date()
        item['CompanyID'] = int(item['CompanyID'])
        item['Open'] = float(item['Open'])
        item['Close'] = float(item['Close'])
        item['Min'] = float(item['Min'])
        item['Max'] = float(item['Max'])
        item['Volume'] = int(item['Volume'])
        item['Amount'] = int(item['Amount'])
        item['market_id'] = market_id

    # for i, row in enumerate(result):
    #     print(row)
    #     if i == 10:
    #         break

    with engine.connect() as conn:
        conn.execute(insert_stmt, result)

# insert_stock_data('Dubai', 'DXB')
# insert_stock_data('AbuDhabi', 'AUH')
# insert_stock_data('Qatar', 'DOH')
# insert_stock_data('Kuwait', 'KW')
# insert_stock_data('Muscat', 'MUS')
# insert_stock_data('Bahrain', 'BHR')
