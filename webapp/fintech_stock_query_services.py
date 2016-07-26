import sqlite3, datetime
from . import config
from .sqlalchemy_models import STOCK_ENTITY_TYPE_TABLE_NAME

###############################
###  Generic DB Functions   ###
###############################
def _get_open_db_connection(use_row_factory=True, register_udfs=False):
    conn = sqlite3.connect(config.NEW_DB_PATH)

    if use_row_factory:
        conn.row_factory = sqlite3.Row

    if register_udfs:
        pass
        # __register_udfs(conn)

    return conn

def _close_db_connection(conn):
    conn.close()

###############################
### General Query Functions ###
###############################
def _fetch_all(sql, *args):
    conn = _get_open_db_connection()
    c = conn.execute(sql, *args) # TODO: Need to understand how this *args really works
    result = c.fetchall()
    _close_db_connection(conn)
    return result

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
          """.format(STOCK_ENTITY_TYPE_TABLE_NAME[set_id], cond=(">=" if direction == 'above' else "<"),
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




