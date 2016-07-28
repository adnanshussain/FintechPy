import sqlite3, datetime
from webapp import config
from webapp.mappings_and_enums import STOCK_ENTITY_TYPE_TABLE_NAME

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

###############################
###  Generic DB Functions   ###
###############################
def _get_open_db_connection(use_row_factory=True, register_udfs=False):
    conn = sqlite3.connect(config.NEW_DB_PATH)

    if use_row_factory:
        conn.row_factory = sqlite3.Row

    if register_udfs:
        _register_udfs(conn)

    return conn

def _close_db_connection(conn):
    conn.close()

def _register_udfs(conn):
    conn.create_function("cp", 2, _udf_change_percentage)
    conn.create_function("dow_name", 1, _udf_day_of_week_name)
    conn.create_function("dow", 1, _udf_day_of_week)
    return conn

###############################
### General Query Functions ###
###############################
def _fetch_all(sql, *args):
    conn = _get_open_db_connection()
    c = conn.execute(sql, *args) # TODO: Need to understand how this *args really works
    result = c.fetchall()
    _close_db_connection(conn)
    return result

################################
### Should be shifted to ORM ###
################################
def get_all_sectors():
    return [dict(id=r[0], name_en=r["name_en"], name_ar=r["name_ar"], short_name_en=r["short_name_en"]) for r in
            _fetch_all("select * from sectors")]

def get_all_companies():
    # TODO: This method can be refactored to have one single method get_all_stock_entites_by_type
    return [dict(value=r["id"], name_en=r["name_en"], name_ar=r["name_en"], text=r["short_name_en"]) for r in
            _fetch_all("select * from companies")]

def get_company(company_id):
    return [dict(id=r["id"], name_en=r["name_en"], name_ar=r["name_ar"], short_name_en=r["short_name_en"]) for r in
            _fetch_all("select * from companies where id = ?", (company_id,))][0]

####################################
### Actual Fintech Core Services ###
####################################
# Q1 Aggregate
def get_the_number_of_times_stockentities_were_upordown_bypercent_in_year_range(set_id, direction, percent, from_yr,
                                                                                 to_yr,
                                                                                 order_by_direction="desc",
                                                                                 top_n=10,
                                                                                 filter_by_sector=None):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=False)

    sql = """
            select t1.stock_entity_id, t2.short_name_en, count(0) frequency from stock_prices t1
            inner join {0} t2 on t1.stock_entity_id = t2.id
              and t1.stock_entity_type_id = ?
            where year >= ? and year <= ?
                and t1.change_percent {cond} ?
            group by t1.stock_entity_id
            order by frequency {order_by_direction}
            LIMIT ?;
          """.format(STOCK_ENTITY_TYPE_TABLE_NAME[set_id], cond=(" >= " if direction == 'above' else " < "),
                     order_by_direction=order_by_direction)

    percent = percent * -1 if direction == 'below' else percent

    # prof = cProfile.Profile()
    # cursor = prof.runcall(conn.execute, sql, (setid, from_yr, to_yr, percent, top_n))
    # prof.print_stats()

    cursor = conn.execute(sql, (set_id, from_yr, to_yr, percent, top_n))

    main_data = [dict(seid=r[0], short_name_en=r[1], frequency=r[2]) for r in cursor.fetchall()]
    result = {'main_data': main_data}

    try:
        average = sum(d['frequency'] for d in main_data) / len(main_data)
    except:
        average = 0

    result['average'] = average

    _close_db_connection(conn)

    return result

# Q1 Individual
def get_the_number_of_times_a_single_stockentity_was_upordown_bypercent_in_year_range(set_id, se_id, direction, percent,
                                                                                      from_yr, to_yr):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=False)

    sql = """
            select year, count(0) frequency
            from stock_prices
            where
                year >= ? and year <= ?
                and stock_entity_type_id = ?
                and stock_entity_id = ?
                and change_percent {cond} ?
            group by year
        """.format(cond=(" >= " if direction == 'above' else " < "))

    percent = percent * -1 if direction == 'below' else percent

    cursor = conn.execute(sql, (from_yr, to_yr, set_id, se_id, percent))

    result = {'main_data': [dict(year=r[0], frequency=r[1]) for r in cursor.fetchall()]}

    # TODO: Find out how to do this with SQLAlchemy...
    cursor = conn.execute("select name_en, name_ar from %s where id = ?" % STOCK_ENTITY_TYPE_TABLE_NAME[set_id], (se_id,))
    data = cursor.fetchone()

    result.update(name_en = data[0], name_ar = data[1])

    _close_db_connection(conn)

    return result

# Q2 Aggregate
def get_the_number_of_times_stock_entities_were_up_down_unchanged_in_year_range(set_id, from_yr, to_yr):
    def calculate_percent(target_number, *args):
        return round(target_number / sum(args) * 100, 2)

    conn = _get_open_db_connection(use_row_factory=False, register_udfs=True)

    sql = '''
            --EXPLAIN QUERY PLAN
            SELECT
                se.short_name_en,
		        count(case when sp.change_percent > 0 then 1 end) positive,
		        count(case when sp.change_percent < 0 then -1 end) negative,
		        count(case when sp.change_percent = 0 then 0 end) no_change,
		        sp.stock_entity_id id
	        from stock_prices sp
	        inner join {0} se on sp.stock_entity_id = se.id
	        where
	          sp.stock_entity_type_id = ?
	        and year >= ? and year <= ?
	        group by sp.stock_entity_id
	        order by positive desc
        '''.format(STOCK_ENTITY_TYPE_TABLE_NAME[set_id])

    cursor = conn.execute(sql, (set_id, from_yr, to_yr))

    result = { 'main_data': [dict(id=r[4], se_short_name_en=r[0], positive=r[1], negative=r[2], nochange=r[3],
                                  percent_positive=calculate_percent(r[1], r[1], r[2], r[3]),
                                  percent_negative=calculate_percent(r[2], r[1], r[2], r[3]),
                                  percent_nochange=calculate_percent(r[3], r[1], r[2], r[3])) for r in cursor.fetchall()]}

    _close_db_connection(conn)

    return result

# Q2 Individual
def get_the_number_of_times_a_stock_entity_was_up_down_unchanged_per_day_in_year_range(set_id, se_id, from_yr, to_yr):
    def calculate_percent(target_number, *args):
        return round(target_number / sum(args) * 100, 2)

    conn = _get_open_db_connection(use_row_factory=False, register_udfs=True)

    sql = '''
            SELECT
		        dow_name(date(sp.for_date)) dow_name,
		        count(case when sp.change_percent > 0 then 1 end) positive,
		        count(case when sp.change_percent < 0 then -1 end) negative,
		        count(case when sp.change_percent = 0 then 0 end) no_change
	        from stock_prices sp
	        where
	        sp.stock_entity_type_id = ?
	        and sp.stock_entity_id = ?
	        and year >= ? and year <= ?
	        group by dow(date(sp.for_date));
        '''

    cursor = conn.execute(sql, (set_id, se_id, from_yr, to_yr))

    result = { 'main_data': [dict(dow_name=r[0], positive=r[1], negative=r[2], nochange=r[3],
                                  percent_positive=calculate_percent(r[1], r[1], r[2], r[3]),
                                  percent_negative=calculate_percent(r[2], r[1], r[2], r[3]),
                                  percent_nochange=calculate_percent(r[3], r[1], r[2], r[3])) for r in cursor.fetchall()]}

    _close_db_connection(conn)

    return result

# Q4 Aggregate
def what_was_the_performance_of_stock_entities_n_days_before_and_after_a_single_day_event(set_id, se_id, date_of_event,
                                                                                          days_before, days_after):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=True)

    sql = """
            select sp1.stock_entity_id, e.name_en, e.name_ar, e.short_name_en, e.short_name_ar,
			      sp2.for_date, sp2.close, cp(sp2.close, sp1.close),
			      sp1.for_date, sp1.close, cp(sp1.close, sp3.close),
			      sp3.for_date, sp3.close
            from stock_prices as sp1
            inner join stock_prices as sp2 on
                sp1.stock_entity_type_id = ?
                {seid}
                and sp1.for_date = ?
                and sp1.stock_entity_type_id = sp2.stock_entity_type_id
                and sp1.stock_entity_id = sp2.stock_entity_id
                and sp2.for_date = (select for_date from stock_prices where stock_entity_type_id = sp1.stock_entity_type_id
                                                and stock_entity_id = sp1.stock_entity_id and for_date < sp1.for_date
                                                order by for_date desc limit 1 offset ?)
            inner join stock_prices sp3 on
                sp1.stock_entity_type_id = sp3.stock_entity_type_id
                and sp1.stock_entity_id = sp3.stock_entity_id
                and sp3.for_date = (select for_date from stock_prices where stock_entity_type_id = sp1.stock_entity_type_id
                                                and stock_entity_id = sp1.stock_entity_id and for_date > sp1.for_date
                                                order by for_date asc limit 1 offset ?)
            inner join {entity} e on
	            sp1.stock_entity_id = e.id;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[set_id], seid='' if se_id is None else 'and sp1.stock_entity_id = ?')

    cursor = conn.execute(sql, (set_id, date_of_event, days_before-1, days_after-1) if se_id  is None
                          else (set_id, se_id, date_of_event, days_before-1, days_after-1))

    result = cursor.fetchall()

    _close_db_connection(conn)

    return result

###############################
### Testing Code...         ###
###############################
# for_date = datetime.datetime.strptime('2015-01-21', '%Y-%m-%d')

def test():
    result = what_was_the_performance_of_stock_entities_n_days_before_and_after_a_single_day_event(1, None, '2015-01-22', 3, 3)

    for r in result:
        print(r)
