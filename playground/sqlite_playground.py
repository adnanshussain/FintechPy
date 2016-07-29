import sqlite3

from webapp.data_access.fintech_services_TBD import TN_FINTECH_CONFIG, TN_SEP_WITH_CHANGE_PERCENTAGE, _udf_change_percentage, \
    _udf_day_of_week, _udf_day_of_week_name, _udf_get_year

conn = sqlite3.connect("webapp/data/argaam_fintech.db")
conn.create_function("cp", 2, _udf_change_percentage)
conn.create_function("dow_name", 1, _udf_day_of_week_name)
conn.create_function("dow", 1, _udf_day_of_week)
conn.create_function("year", 1, _udf_get_year)

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

    if cursor.fetchone()[0] == 0: # FintechConfig table does not exist
        sql = "CREATE TABLE {0} ('StockEntityPriceLastCount' INTEGER)".format(TN_FINTECH_CONFIG)
        conn.execute(sql)
        sql = "INSERT INTO {0} (StockEntityPriceLastCount) VALUES (?)".format(TN_FINTECH_CONFIG)
        conn.execute(sql, (0, ))
    else: # FintechConfig table does exists
        sql = "SELECT StockEntityPriceLastCount FROM {0}".format(TN_FINTECH_CONFIG)
        cursor = conn.execute(sql)
        sep_last_count = cursor.fetchone()[0]

    sql = "SELECT count(0) FROM StockEntityPrices"
    cursor = conn.execute(sql)
    sep_current_count = cursor.fetchone()[0]

    if sep_last_count == 0: # The recorded se prices last count was zero
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

    elif sep_current_count != sep_last_count: # The recorded se prices last count was <> current prices count
        sql = "drop table {0}".format(TN_SEP_WITH_CHANGE_PERCENTAGE)
        conn.execute(sql)

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
    else:
        print("Do nothing, all is OK")

    conn.commit()
    conn.close()
except sqlite3.OperationalError as op_err:
    print(op_err)
    raise op_err

