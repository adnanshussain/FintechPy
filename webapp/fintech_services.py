import sqlite3, datetime
from . import config

STOCK_ENTITY_TYPES = dict(
    company = 1,
    market = 2,
    sector = 3
)

###############################
### Table Names             ###
###############################
TN_FINTECH_CONFIG = "FintechConfig"
TN_SEP_WITH_CHANGE_PERCENTAGE = "StockEntityPricesWithChangePercentage"

###############################
### User Defined Functions  ###
###############################
def _udf_change_percentage(y1, y2):
    return ((y2 - y1) / y1) * 100

def _udf_day_of_week_name(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    return datetime.date(year, month, day).strftime("%A")

def _udf_day_of_week(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    return int(datetime.date(year, month, day).strftime("%w"))

def _udf_get_year(dt):
    try:
        return datetime.datetime.strptime(dt, '%Y-%m-%d').year
    except Exception as err:
        print(err)

###############################
###  Generic DB Functions   ###
###############################
def __get_open_db_connection(use_row_factory=True, register_udfs=False):
    conn = sqlite3.connect(config.DB_PATH)

    if use_row_factory:
        conn.row_factory = sqlite3.Row

    if register_udfs:
        __register_udfs(conn)

    return conn

def __close_db_connection(conn):
    conn.close()

def __register_udfs(conn):
    conn.create_function("cp", 2, _udf_change_percentage)
    conn.create_function("dow_name", 1, _udf_day_of_week_name)
    conn.create_function("dow", 1, _udf_day_of_week)
    conn.create_function("year", 1, _udf_get_year)
    return conn

###############################
### General Query Functions ###
###############################
def __fetch_all(sql, *args):
    conn = __get_open_db_connection()
    c = conn.execute(sql, *args) # TODO: Need to understand how this *args really works
    result = c.fetchall()
    __close_db_connection(conn)
    return result

def get_all_stock_entity_types():
    return [dict(id=r[0], name=r[1]) for r in __fetch_all("select * from StockEntityTypes")]

def get_all_sectors():
    return [dict(id=r[0], name_en=r["NameEn"], name_ar=r["NameAr"], short_name_en=r["ShortNameEn"]) for r in
            __fetch_all("select * from StockEntities where StockEntityTypeID = ?", (STOCK_ENTITY_TYPES["sector"],))]

##################################
### Fintech Specific Functions ###
##################################
def __get_temp_table_name(setid, seid):
    return "sep_" + str(setid) + "_" + str(seid)

def __create_table_with_change_percentage(sep_current_count, conn):
    sql = "UPDATE {0} SET StockEntityPriceLastCount = ?".format(TN_FINTECH_CONFIG)
    conn.execute(sql, (sep_current_count, ))

    # This is the alternative for getting rowid() as in sql server
    sql = """
        create temp table {0}
        AS
            select *
            from StockEntityPrices
            order by  StockEntityTypeID, StockEntityID, ForDate;
        """.format(TN_SEP_WITH_CHANGE_PERCENTAGE + "_ROWIDS")
    conn.execute(sql)

    # Now using the rowid compute the change percentage
    sql = """
        create table {0}
            AS
            select
                t2.StockEntityTypeID, t2.StockEntityID, date(t2.fordate) fordate,
                CAST(strftime('%Y', date(t2.fordate)) as INTEGER) as yr,
                dow_name(date(t2.fordate)) the_dow, t2.close,
                -- cp(t1.close, t2.close) as change_percentage
                ((t2.close - t1.close) / t1.close) * 100 as change_percentage
            from {ttn} t1 inner join {ttn} t2 on
                t1.StockEntityTypeID = t2.StockEntityTypeID
                and t1.StockEntityID = t2.StockEntityID
                and t1.rowid = t2.rowid - 1;
            """.format(TN_SEP_WITH_CHANGE_PERCENTAGE, ttn=(TN_SEP_WITH_CHANGE_PERCENTAGE + "_ROWIDS"))

    conn.execute(sql)

def __check_and_create_table_with_change_percentage(setid, from_yr, to_yr, conn):
    try:
        # sql = "drop table {0}".format(TN_FINTECH_CONFIG)
        # conn.execute(sql)
        # sql = "drop table {0}".format(TN_SEP_WITH_CHANGE_PERCENTAGE + "_ROWIDS")
        # conn.execute(sql)
        # sql = "drop table {0}".format(TN_SEP_WITH_CHANGE_PERCENTAGE)
        # conn.execute(sql)
        #
        # conn.commit()

        sep_last_count = 0

        sql = "SELECT count(0) FROM sqlite_master WHERE type='table' AND name = ?"
        cursor = conn.execute(sql, (TN_FINTECH_CONFIG, ))

        # If FintechConfig table does not exist, create it and inititalize it to zero
        if cursor.fetchone()[0] == 0:
            sql = "CREATE TABLE {0} ('StockEntityPriceLastCount' INTEGER)".format(TN_FINTECH_CONFIG)
            conn.execute(sql)
            sql = "INSERT INTO {0} (StockEntityPriceLastCount) VALUES (?)".format(TN_FINTECH_CONFIG)
            conn.execute(sql, (0, ))
        # If FintechConfig table does exists, get the last recorded count
        else:
            sql = "SELECT StockEntityPriceLastCount FROM {0}".format(TN_FINTECH_CONFIG)
            cursor = conn.execute(sql)
            sep_last_count = cursor.fetchone()[0]

        # Get the current count of rows in the SEP table
        sql = "SELECT count(0) FROM StockEntityPrices"
        cursor = conn.execute(sql)
        sep_current_count = cursor.fetchone()[0]

        # If the last recorded count was zero
        if sep_last_count == 0:
            __create_table_with_change_percentage(sep_current_count, conn)
        elif sep_current_count != sep_last_count: # The recorded se prices last count was <> current prices count
            sql = "drop table {0}".format(TN_SEP_WITH_CHANGE_PERCENTAGE)
            conn.execute(sql)

            __create_table_with_change_percentage(sep_current_count, conn)
        else:
            print("Do nothing, all is OK")

        conn.commit()
    except sqlite3.OperationalError as op_err:
        print(op_err)
        raise op_err

###############################
###  Fintech Query Funtions ###
###############################
def get_number_of_times_stockentities_that_were_upordown_bypercent_in_year_range(setid, direction, percent, from_yr, to_yr,
                                                                                 order_by_direction="desc",
                                                                                 top_n=10,
                                                                                 filter_by_sector=None):
    conn = __get_open_db_connection(use_row_factory=False, register_udfs=True)

    __check_and_create_table_with_change_percentage(setid, from_yr, to_yr, conn)

    sql = """
            select t1.StockEntityID, t2.ShortNameEn, count(0) frequency from {0} t1
            inner join StockEntities t2 on t2.StockEntityID = t1.StockEntityID
                and t2.StockEntityTypeID = ?
            where yr >= ? and yr <= ?
                and change_percentage {cond} ?
            group by t1.StockEntityID
            order by frequency {order_by_direction}
            LIMIT ?;
          """.format(TN_SEP_WITH_CHANGE_PERCENTAGE, cond=(">=" if direction == 'above' else "<"),
                     order_by_direction=order_by_direction)

    cursor = conn.execute(sql, (setid, from_yr, to_yr, percent, top_n))

    result = [dict(seid=r[0],short_name_en=r[1],frequency=r[2]) for r in cursor.fetchall()]

    __close_db_connection(conn)

    return result

def q1_stockentity_was_upordown_bysomepercent_induration(setid, seid, cp, from_yr, to_yr):
    '''
        Gets the list of dates when a Stock Entity(ies) was/were up or down by a given percentage within
        the specified time duration
    '''

    conn = __get_open_db_connection(use_row_factory=False, register_udfs=True)

    temp_table_name = __get_temp_table_name(setid, seid)

    __create_temp_table_with_closing_percentage(setid, seid, from_yr, to_yr, temp_table_name, conn)

    cursor = conn.execute("""select
                            *
                            from {0}
                            where
                            yr >= ? and yr <= ?
                            and change_percentage {cond} ?;
                        """.format(temp_table_name, cond=(">=" if cp >= 0 else "<=")), (from_yr, to_yr, cp))

    if config.DEBUG:
        for r in cursor:
            print(r)

    result = [dict(seid=r[0],fordate=r[1],year=r[2],dow=r[3],closing_price=r[4],change_percentage=r[5]) for r in cursor.fetchall()]

    __close_db_connection(conn)

    return result