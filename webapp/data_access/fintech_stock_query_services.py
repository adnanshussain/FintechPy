import functools
from webapp.data_access import _get_open_db_connection, _close_db_connection, _fetch_all
from webapp.data_access.mappings_and_enums import STOCK_ENTITY_TYPE_TABLE_NAME

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
            SELECT
              sp1.stock_entity_id,
              e.name_en,
              e.name_ar,
              e.short_name_en,
              e.short_name_ar,
              sp2.for_date,
              sp2.close,
              cp(sp2.close, sp1.close),
              sp1.for_date,
              sp1.close,
              cp(sp1.close, sp3.close),
              sp3.for_date,
              sp3.close
            FROM stock_prices AS sp1
              INNER JOIN stock_prices AS sp2
              INNER JOIN stock_prices sp3
              INNER JOIN {entity} e ON
                                       sp1.stock_entity_type_id = 1
                                       {seid}
                                       AND sp1.for_date > date(:doe, '-1 months')
                                       AND sp1.for_date <= :doe
                                       AND sp2.for_date > date(:doe, '-1 months')
                                       AND sp2.for_date < :doe
                                       AND sp3.for_date > :doe
                                       AND sp3.for_date <= date(:doe, '1 months')

                                       AND sp2.stock_entity_type_id = sp1.stock_entity_type_id
                                       AND sp2.stock_entity_id = sp1.stock_entity_id
                                       AND sp3.stock_entity_type_id = sp1.stock_entity_type_id
                                       AND sp3.stock_entity_id = sp1.stock_entity_id

                                       AND sp1.for_date = (SELECT for_date
                                                           FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                                           WHERE for_date > date(:doe, '-1 months')
                                                                 AND for_date <= :doe
                                                                 AND stock_entity_id = sp1.stock_entity_id
                                                                 AND stock_entity_type_id = sp1.stock_entity_type_id
                                                           LIMIT 1)
                                       AND sp2.for_date = (SELECT for_date
                                                           FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                                           WHERE for_date > date(:doe, '-1 months')
                                                                 AND for_date < :doe
                                                                 AND stock_entity_id = sp1.stock_entity_id
                                                                 AND stock_entity_type_id = sp1.stock_entity_type_id
                                                           LIMIT 1 OFFSET :days_before)
                                       AND sp3.for_date = (SELECT for_date
                                                           FROM stock_prices INDEXED BY idx_sp_dt_asc_setid_asc
                                                           WHERE for_date < date(:doe, '1 months')
                                                                 AND for_date > :doe
                                                                 AND stock_entity_id = sp1.stock_entity_id
                                                                 AND stock_entity_type_id = sp1.stock_entity_type_id
                                                           LIMIT 1 OFFSET :days_after)
                                       AND sp1.stock_entity_id = e.id;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[set_id], seid='' if se_id is None else 'and sp1.stock_entity_id = :seid')

    params = { "setid":set_id, "doe": date_of_event, "days_before":days_before-1, "days_after": days_after-1}
    if se_id is not None:
        params.update({"seid": se_id})

    cursor = conn.execute(sql, params)

    result = { 'main_data': [dict(name_en=r[1], cp_before=r[7], cp_after=r[10]) for r in cursor.fetchall()] }

    _close_db_connection(conn)

    return result

def what_is_the_effect_of_event_group_on_stock_entities(set_id, event_group_id, days_before, days_after):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=True)

    days_before -= 1
    days_after -= 1
    date_margin_of_error_back = '-14 days'
    date_margin_of_error_forward = '14 days'

    sql_pre_req = """
                    CREATE TEMP TABLE tt_sp AS
                      SELECT
                        ev.id event_id,
                        ev.starts_on,
                        ev.ends_on,
                        sp.stock_entity_id,
                        sp.for_date,
                        sp.close
                      FROM events ev
                        INNER JOIN stock_prices sp
                          ON
                            ev.event_group_id = :egid
                            AND sp.stock_entity_type_id = :setid
                            --AND sp.stock_entity_id = 46
                            AND sp.for_date > date(ev.starts_on, :dmoeb)
                            AND ((ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, :dmoef))
                                 OR (ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, :dmoef)));
           """
    params = {"setid": set_id, "egid": event_group_id, "dmoeb": date_margin_of_error_back, "dmoef": date_margin_of_error_forward}
    conn.execute(sql_pre_req, params)

    sql_pre_req = "create index tt_idx_sp_dt_desc_seid on tt_sp (for_date DESC, stock_entity_id);"
    conn.execute(sql_pre_req)

    sql_pre_req = "create index tt_idx_sp_dt_asc_seid on tt_sp (for_date ASC, stock_entity_id);"
    conn.execute(sql_pre_req)

    sql_pre_req = """
                    create TEMP TABLE tt_sp_before_ev AS
                      SELECT
                        ev.id event_id,
                        ev.type,
                        ev.starts_on,
                        ev.ends_on,
                        sp.stock_entity_id,
                        sp.for_date,
                        sp.close
                      FROM events ev
                        INNER JOIN tt_sp sp
                          ON
                            ev.id = sp.event_id
                            AND sp.for_date > date(ev.starts_on, :dmoeb)
                            AND sp.for_date < ev.starts_on
                            AND sp.for_date = (SELECT for_date
                                                      FROM tt_sp INDEXED BY tt_idx_sp_dt_desc_seid
                                                      WHERE stock_entity_id = sp.stock_entity_id
                                                            AND event_id = ev.id
                                                            AND for_date > date(ev.starts_on, :dmoeb)
                                                            AND for_date < ev.starts_on
                                                      LIMIT 1 OFFSET :days_before);
                """
    params = {"dmoeb": date_margin_of_error_back, "dmoef": date_margin_of_error_forward, "days_before": days_before}
    conn.execute(sql_pre_req, params)

    sql_pre_req = """
                    create TEMP TABLE tt_sp_ev_start AS
                      SELECT
                        ev.id event_id,
                        ev.type type,
                        ev.starts_on starts_on,
                        ev.ends_on ends_on,
                        sp.stock_entity_id stock_entity_id,
                        max(sp.for_date) for_date,
                        sp.close close
                      FROM events ev
                        INNER JOIN tt_sp sp INDEXED BY tt_idx_sp_dt_desc_seid
                          ON
                            ev.id = sp.event_id
                            and sp.for_date > date(ev.starts_on, :dmoeb)
                            AND sp.for_date <= ev.starts_on
                      GROUP BY ev.id, ev.type, ev.starts_on, ev.ends_on, sp.stock_entity_id;
                  """
    params = {"dmoeb": date_margin_of_error_back}
    conn.execute(sql_pre_req, params)

    sql_pre_req = """
                    create TEMP TABLE tt_sp_ev_end AS
                      SELECT
                        ev.id event_id,
                        ev.type type,
                        ev.starts_on starts_on,
                        ev.ends_on ends_on,
                        sp.stock_entity_id stock_entity_id,
                        max(sp.for_date) for_date,
                        sp.close close
                      FROM events ev
                        INNER JOIN tt_sp sp INDEXED BY tt_idx_sp_dt_desc_seid
                          ON
                            ev.id = sp.event_id
                            AND
                            ((ev.ends_on IS NULL AND sp.for_date > date(ev.starts_on, :dmoeb) AND sp.for_date <= ev.starts_on)
                             OR
                             (ev.ends_on IS NOT NULL AND sp.for_date > ev.starts_on AND sp.for_date <= ev.ends_on))
                      GROUP BY ev.id, ev.type, ev.starts_on, ev.ends_on, sp.stock_entity_id;
                  """
    params = {"dmoeb": date_margin_of_error_back}
    conn.execute(sql_pre_req, params)

    sql_pre_req = """
                    create TEMP TABLE tt_sp_after_ev AS
                      SELECT
                        ev.id event_id,
                        ev.type,
                        ev.starts_on,
                        ev.ends_on,
                        sp.stock_entity_id,
                        sp.for_date,
                        sp.close
                      FROM events ev
                        INNER JOIN tt_sp sp
                          ON
                            ev.id = sp.event_id
                            AND
                            ((ev.ends_on IS NULL AND sp.for_date > ev.starts_on AND sp.for_date < date(ev.starts_on, :dmoef))
                              OR (ev.ends_on IS NOT NULL AND sp.for_date > ev.ends_on AND sp.for_date < date(ev.ends_on, :dmoef)))
                             AND sp.for_date =
                                 (SELECT sp_inner.for_date
                                  FROM tt_sp sp_inner INDEXED BY tt_idx_sp_dt_asc_seid
                                  WHERE
                                        sp_inner.stock_entity_id = sp.stock_entity_id
                                        AND event_id = ev.id
                                        AND
                                        ((ev.ends_on IS NULL AND sp_inner.for_date > ev.starts_on AND sp_inner.for_date < date(ev.starts_on, :dmoef))
                                        OR
                                         (ev.ends_on IS NOT NULL AND sp_inner.for_date > ev.ends_on AND sp_inner.for_date < date(ev.ends_on, :dmoef)))
                                  LIMIT 1 OFFSET :days_after);
                              """
    params = {"dmoef": date_margin_of_error_forward, "days_after": days_after}
    conn.execute(sql_pre_req, params)

    sql_pre_req = """
                    CREATE TEMP TABLE tt_source AS
                    SELECT
                      ae.stock_entity_id stock_entity_id,
                      e.short_name_en short_name_en,
                      be_se_ee.before_dt before_date,
                      be_se_ee.before_close before_close,
                      be_se_ee.start_date start_date,
                      be_se_ee.start_close start_close,
                      be_se_ee.end_date  end_date,
                      be_se_ee.end_close end_close,
                      ae.for_date        after_date,
                      ae.close           after_close
                    FROM tt_sp_after_ev ae
                      INNER JOIN {entity} e
                      INNER JOIN
                      (SELECT
                         ee.event_id,
                         ee.stock_entity_id,
                         ee.starts_on,
                         ee.ends_on,
                         be_se.before_dt,
                         be_se.before_close,
                         be_se.start_date,
                         be_se.start_close,
                         ee.for_date end_date,
                         ee.close    end_close
                       FROM tt_sp_ev_end ee
                         INNER JOIN (
                                      SELECT
                                        be.event_id,
                                        be.stock_entity_id,
                                        be.for_date before_dt,
                                        be.close    before_close,
                                        se.for_date start_date,
                                        se.close    start_close
                                      FROM tt_sp_before_ev be
                                        INNER JOIN tt_sp_ev_start se
                                          ON
                                            be.event_id = se.event_id
                                            AND be.stock_entity_id = se.stock_entity_id) be_se
                           ON
                             ee.event_id = be_se.event_id
                             AND ee.stock_entity_id = be_se.stock_entity_id) be_se_ee
                        ON
                          e.id = ae.stock_entity_id
                          AND ae.event_id = be_se_ee.event_id
                          AND ae.stock_entity_id = be_se_ee.stock_entity_id
                          ORDER BY ae.starts_on;
                        """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[set_id])
    conn.execute(sql_pre_req)

    sql = """
            select
                    stock_entity_id,
                            short_name_en,

                    count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_before,

                    sum((start_close - before_close) / before_close * 100.00) up_agg_perf_before,

                    count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_before,

                    count(case when ((end_close - start_close) / start_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((end_close - start_close) / start_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((end_close - start_close) / start_close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_between,

                    sum((end_close - start_close) / start_close * 100.00) up_agg_perf_between,

                    count(case when ((end_close - start_close) / start_close) * 100 < 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((end_close - start_close) / start_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((end_close - start_close) / start_close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_between,

                    count(case when ((after_close - end_close) / end_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((after_close - end_close) / end_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((after_close - end_close) / end_close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_after,

                    sum((after_close - end_close) / end_close * 100.00) up_agg_perf_after,

                    count(case when ((after_close - end_close) / end_close) * 100 < 0 then 1 else NULL end) * 1.0 /
                    (count(case when ((after_close - end_close) / end_close) * 100 >= 0 then 1 else NULL end) +
                     count(case when ((after_close - end_close) / end_close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_after
            from tt_source
            GROUP BY stock_entity_id
            ORDER BY up_prob_before desc, up_prob_after desc
            limit 40;
          """
    cursor = conn.execute(sql)

    result_1 = [dict(id=r[0], name_en=r[1], up_prob_before=r[2], up_aggr_perf_before=r[3], down_prob_before=r[4],
                     up_prob_between=r[5], up_aggr_perf_between=r[6], down_prob_between=r[7],
                     up_prob_after=r[8], up_aggr_perf_after=r[9], down_prob_after=r[10]
                     ) for r in cursor.fetchall()]

    _close_db_connection(conn)

    # result_1.sort(key=lambda k: k['up_prob_before'], reverse=True)

    result = { 'main_data': result_1 }

    up_prob_between_count = sum(1 for r in result_1 if r['up_prob_between'] < 100)
    down_prob_between_count = sum(1 for r in result_1 if r['down_prob_between'] > 0)

    if up_prob_between_count == 0 and down_prob_between_count == 0:
        result.update({ 'has_range_events': False })
    else:
        result.update({'has_range_events': True})

    return result

def what_was_the_effect_of_an_event_group_on_a_stock_entity(setid, seid, egid, days_before, days_after):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=False)

    days_before -= 1
    days_after -= 1
    date_margin_of_error_back = '-14 days'
    date_margin_of_error_forward = '14 days'

    sql = """
            SELECT
              sp_evs.stock_entity_id,
              e.short_name_en,

              sp_bev.for_date         AS                           before_date,
              sp_bev.close    AS                                   before_close,
              ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 cp_before,

              sp_evs.for_date AS                                   start_date,
              sp_evs.close    AS                                   start_close,
              ((sp_eve.close - sp_evs.close) / sp_evs.close) * 100 cp_between,

              sp_eve.for_date AS                                   end_date,
              sp_eve.close    AS                                   end_close,
              ((sp_aev.close - sp_eve.close) / sp_eve.close) * 100 cp_after,

              sp_aev.for_date AS                                   after_date,
              sp_aev.close    AS                                   after_close
            FROM stock_prices AS sp_evs
              INNER JOIN stock_prices AS sp_bev
              INNER JOIN stock_prices AS sp_eve
              INNER JOIN stock_prices AS sp_aev
              INNER JOIN events AS ev
              INNER JOIN {entity} AS e
                ON
                  sp_evs.stock_entity_type_id = :setid
                  AND ev.event_group_id = :egid
                  AND sp_evs.stock_entity_id = :seid

                  and sp_bev.for_date > date(ev.starts_on, :dmoeb)
                  and sp_bev.for_date < ev.starts_on
                  and sp_evs.for_date > date(ev.starts_on, :dmoeb)
                  and sp_evs.for_date <= ev.starts_on
                  and ((ev.ends_on is NULL and sp_eve.for_date > date(ev.starts_on, :dmoeb) and sp_evs.for_date <= ev.starts_on)
                    OR
                       (ev.ends_on is not NULL and sp_eve.for_date > ev.starts_on and sp_evs.for_date <= ev.ends_on))
                  and ((ev.ends_on is NULL and sp_aev.for_date > ev.starts_on and sp_evs.for_date < date(ev.starts_on, :dmoef))
                    OR
                       (ev.ends_on is not NULL and sp_aev.for_date > ev.ends_on and sp_evs.for_date < date(ev.ends_on, :dmoef)))

                  AND sp_evs.stock_entity_type_id = sp_bev.stock_entity_type_id
                  AND sp_evs.stock_entity_id = sp_bev.stock_entity_id
                  AND sp_evs.stock_entity_type_id = sp_aev.stock_entity_type_id
                  AND sp_evs.stock_entity_id = sp_aev.stock_entity_id
                  AND sp_evs.stock_entity_type_id = sp_eve.stock_entity_type_id
                  AND sp_evs.stock_entity_id = sp_eve.stock_entity_id

                  AND sp_evs.for_date = (SELECT for_date
                                               FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                               WHERE for_date > DATE(ev.starts_on, :dmoeb)
                                                     AND for_date <= ev.starts_on
                                                     AND stock_entity_id = sp_evs.stock_entity_id
                                                     AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                               LIMIT 1)

                  AND sp_bev.for_date = (SELECT for_date
                                                  FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                                  WHERE for_date > DATE(ev.starts_on, :dmoeb)
                                                        AND for_date < ev.starts_on
                                                        AND stock_entity_id = sp_evs.stock_entity_id
                                                        AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                                  LIMIT 1 OFFSET :days_before)

                  AND ((ev.ends_on IS NOT NULL
                        AND sp_eve.for_date = (SELECT for_date
                                                   FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                                   WHERE for_date > DATE(ev.starts_on)
                                                         AND for_date <= ev.ends_on
                                                         AND stock_entity_id = sp_evs.stock_entity_id
                                                         AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                                   LIMIT 1))
                       OR
                       (ev.ends_on IS NULL AND sp_eve.for_date = sp_evs.for_date))

                  AND sp_aev.for_date = (SELECT for_date
                                                 FROM stock_prices INDEXED BY idx_sp_dt_asc_setid_asc
                                                 WHERE
                                                   ((ev.ends_on IS NOT NULL AND for_date < DATE(ev.ends_on, :dmoef))
                                                    OR
                                                    (ev.ends_on IS NULL AND for_date < DATE(ev.starts_on, :dmoef)))
                                                   AND
                                                   ((ev.ends_on IS NOT NULL AND for_date > ev.ends_on)
                                                    OR
                                                    (ev.ends_on IS NULL AND for_date > ev.starts_on))
                                                   AND stock_entity_id = sp_evs.stock_entity_id
                                                   AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                                 LIMIT 1 OFFSET :days_after)

                  AND sp_evs.stock_entity_id = e.id
            ORDER BY ev.starts_on;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[setid])

    # print(sql)

    params = {"setid": setid, "seid": seid, "egid": egid, "days_before": days_before, "days_after": days_after,
              "dmoeb": date_margin_of_error_back, "dmoef": date_margin_of_error_forward}

    cursor = conn.execute(sql, params)

    result_1 = [dict(id=r[0], name_en=r[1], perf_before=r[4], perf_between=r[7], perf_after=r[10], event_date=r[5]) for r in cursor.fetchall()]

    up_times_before = sum(1 for r in result_1 if r['perf_before'] >= 0)
    down_times_before = sum(1 for r in result_1 if r['perf_before'] < 0)
    up_times_between = sum(1 for r in result_1 if r['perf_between'] >= 0)
    down_times_between = sum(1 for r in result_1 if r['perf_between'] < 0)
    up_times_after = sum(1 for r in result_1 if r['perf_after'] >= 0)
    down_times_after = sum(1 for r in result_1 if r['perf_after'] < 0)

    result = { 'main_data': result_1,
               'ap_before': sum(r['perf_before'] for r in result_1),
               'ap_between': sum(r['perf_between'] for r in result_1),
               'ap_after': sum(r['perf_after'] for r in result_1),
               'up_prob_before': up_times_before / (up_times_before + down_times_before) * 100,
               'down_prob_before': down_times_before / (up_times_before + down_times_before) * 100,
               'up_prob_between': up_times_between / (up_times_between + down_times_between) * 100,
               'down_prob_between': down_times_between / (up_times_between + down_times_between) * 100,
               'up_prob_after': up_times_after / (up_times_after + down_times_after) * 100,
               'down_prob_after': down_times_after / (up_times_after + down_times_after) * 100
               }

    _close_db_connection(conn)

    return result

###############################
### Testing Code...         ###
###############################
# for_date = datetime.datetime.strptime('2015-01-21', '%Y-%m-%d')

def test():
    # result = what_was_the_effect_of_an_event_group_on_a_stock_entity(1, 22, 2, 3, 3)
    result = what_is_the_effect_of_event_group_on_stock_entities(1, 2, 3, 3)

    for r in result['main_data']:
        print(r)

    for k, v in result.items():
        print(k, v)

# test()

