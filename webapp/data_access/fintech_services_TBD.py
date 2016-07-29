import sqlite3, datetime
from webapp import config

import cProfile

STOCK_ENTITY_TYPES = dict(
    company = 1,
    market = 2,
    sector = 3,
    commodities = 5
)

def profile_code(method):
    def wrapper(*args, **kw):
        import cProfile, pstats, io
        pr = cProfile.Profile()
        pr.enable()

        result = method(*args, **kw)

        pr.disable()
        # s = io.StringIO()
        # sortby = 'cumulative'
        # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps = pstats.Stats(pr)
        ps.print_stats()
        # print(s.getvalue())

        return result
    return wrapper

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
    conn = sqlite3.connect(config.OLD_DB_PATH)

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

def get_all_companies():
    # TODO: This method can be refactored to have one single method get_all_stock_entites_by_type
    return [dict(value=r[0], name_en=r["NameEn"], name_ar=r["NameAr"], text=r["ShortNameEn"]) for r in
            __fetch_all("select * from StockEntities where StockEntityTypeID = ?", (STOCK_ENTITY_TYPES["company"],))]

def get_company(company_id):
    return [dict(id=r[0], name_en=r["NameEn"], name_ar=r["NameAr"], short_name_en=r["ShortNameEn"]) for r in
            __fetch_all("select * from StockEntities where StockEntityTypeID = ? and StockEntityID = ?",
                        (STOCK_ENTITY_TYPES["company"], company_id))][0]

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

    # TODO: Drop the index on SEPWCP on StockEntityID column

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

    # TODO: Drop the SEPWCP_ROWIDS Table, it's an intermediary table
    # TODO: Create the index on SEPWCP on StockEntityID column

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
# @profile_code
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

    percent = percent * -1 if direction == 'below' else percent

    # prof = cProfile.Profile()
    # cursor = prof.runcall(conn.execute, sql, (setid, from_yr, to_yr, percent, top_n))
    # prof.print_stats()

    cursor = conn.execute(sql, (setid, from_yr, to_yr, percent, top_n))

    main_data = [dict(seid=r[0],short_name_en=r[1],frequency=r[2]) for r in cursor.fetchall()]
    result = { 'main_data': main_data }

    try:
        average = sum(d['frequency'] for d in main_data) / len(main_data)
    except:
        average = 0

    result['average'] = average

    __close_db_connection(conn)

    return result

def get_number_of_times_a_single_stockentity_was_upordown_bypercent_in_year_range(setid, seid, direction, percent,
                                                                                  from_yr, to_yr):
    conn = __get_open_db_connection(use_row_factory=False, register_udfs=True)

    __check_and_create_table_with_change_percentage(setid, from_yr, to_yr, conn)

    sql = """select
                yr, count(0) frequency
                from {0}
                where
                yr >= ? and yr <= ?
                and change_percentage {cond} ?
                and StockEntityTypeID = ?
                and StockEntityID = ?
                group by yr
            """.format(TN_SEP_WITH_CHANGE_PERCENTAGE, cond=(">=" if direction == 'above' else "<"))

    percent = percent * -1 if direction == 'below' else percent

    cursor = conn.execute(sql, (from_yr, to_yr, percent, setid, seid))

    result = { 'main_data': [dict(year=r[0], frequency=r[1]) for r in cursor.fetchall()],
               'company_name_ar': [x for x in get_all_companies() if x['value'] == seid ][0]['name_ar']}

    __close_db_connection(conn)

    return result

def get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(setid, from_yr, to_yr):
    def calculate_percent(target_number, *args):
        return round(target_number / sum(args) * 100, 2)

    conn = __get_open_db_connection(use_row_factory=False, register_udfs=True)

    __check_and_create_table_with_change_percentage(setid, from_yr, to_yr, conn)

    sql = '''
            --EXPLAIN QUERY PLAN
            SELECT
                se.ShortNameEn short_name_en,
		        --dow_name(date(spv.fordate)) Day,
		        count(case when spv.change_percentage > 0 then 1 end) positive,
		        count(case when spv.change_percentage < 0 then -1 end) negative,
		        count(case when spv.change_percentage = 0 then 0 end) no_change,
		        se.StockEntityID id
	        from {0} spv
	        inner join StockEntities se on se.StockEntityTypeID = spv.StockEntityTypeID and se.StockEntityID = spv.StockEntityID
	        where
	        spv.StockEntityTypeID = ?
	        and yr >= ? and yr <= ?
	        group by spv.StockEntityID --, dow(date(spv.fordate))
	        --order by StockEntityID, dow(date(spv.fordate))
	        order by positive desc
        '''.format(TN_SEP_WITH_CHANGE_PERCENTAGE)

    cursor = conn.execute(sql, (setid, from_yr, to_yr))

    result = { 'main_data': [dict(id=r[4], se_short_name_en=r[0], positive=r[1], negative=r[2], nochange=r[3],
                                  percent_positive=calculate_percent(r[1], r[1], r[2], r[3]),
                                  percent_negative=calculate_percent(r[2], r[1], r[2], r[3]),
                                  percent_nochange=calculate_percent(r[3], r[1], r[2], r[3])) for r in cursor.fetchall()]}

    __close_db_connection(conn)

    return result

def get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(setid, seid, from_yr, to_yr):
    def calculate_percent(target_number, *args):
        return round(target_number / sum(args) * 100, 2)

    conn = __get_open_db_connection(use_row_factory=False, register_udfs=True)

    __check_and_create_table_with_change_percentage(setid, from_yr, to_yr, conn)

    sql = '''
            SELECT
		        dow_name(date(spv.fordate)) dow_name,
		        count(case when spv.change_percentage > 0 then 1 end) positive,
		        count(case when spv.change_percentage < 0 then -1 end) negative,
		        count(case when spv.change_percentage = 0 then 0 end) no_change
	        from {0} spv
	        where
	        spv.StockEntityTypeID = ?
	        and spv.StockEntityID = ?
	        and yr >= ? and yr <= ?
	        group by dow(date(spv.fordate));
        '''.format(TN_SEP_WITH_CHANGE_PERCENTAGE)

    cursor = conn.execute(sql, (setid, seid, from_yr, to_yr))

    result = { 'main_data': [dict(dow_name=r[0], positive=r[1], negative=r[2], nochange=r[3],
                                  percent_positive=calculate_percent(r[1], r[1], r[2], r[3]),
                                  percent_negative=calculate_percent(r[2], r[1], r[2], r[3]),
                                  percent_nochange=calculate_percent(r[3], r[1], r[2], r[3])) for r in cursor.fetchall()]}

    __close_db_connection(conn)

    return result
