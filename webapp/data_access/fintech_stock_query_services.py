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
            select sp1.stock_entity_id, e.name_en, e.name_ar, e.short_name_en, e.short_name_ar,
			      sp2.for_date, sp2.close, cp(sp2.close, sp1.close),
			      sp1.for_date, sp1.close, cp(sp1.close, sp3.close),
			      sp3.for_date, sp3.close
            from stock_prices as sp1
            inner join stock_prices as sp2
            inner join stock_prices sp3
            inner join {entity} e on
                sp1.stock_entity_type_id = :setid
                --and sp1.stock_entity_id IN (SELECT id from companies LIMIT 10)
                {seid}
                and sp1.for_date > date(:doe, '-1 months')
                and sp1.for_date < date(:doe, '1 months')

                and sp1.stock_entity_type_id = sp2.stock_entity_type_id
                and sp1.stock_entity_id = sp2.stock_entity_id
                and sp1.stock_entity_type_id = sp3.stock_entity_type_id
                and sp1.stock_entity_id = sp3.stock_entity_id

                and sp1.for_date = (select for_date from stock_prices
                                        where for_date > date(:doe, '-1 months')
                                        and for_date <= :doe
                                        and stock_entity_id = sp1.stock_entity_id
                                        and stock_entity_type_id = sp1.stock_entity_type_id
                                        ORDER BY for_date DESC LIMIT 1)
                and sp2.for_date = (select for_date from stock_prices
                                        where for_date > date(:doe, '-1 months')
                                        and	for_date < sp1.for_date
                                        and stock_entity_id = sp1.stock_entity_id
                                        and stock_entity_type_id = sp1.stock_entity_type_id
                                        order by for_date desc limit 1 offset :days_before)
                and sp3.for_date = (select for_date from stock_prices
                                        where for_date < date(:doe, '1 months')
                                        and for_date > sp1.for_date
                                        and stock_entity_id = sp1.stock_entity_id
                                        and stock_entity_type_id = sp1.stock_entity_type_id
                                        order by for_date asc limit 1 offset :days_after)

	            and sp1.stock_entity_id = e.id;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[set_id], seid='' if se_id is None else 'and sp1.stock_entity_id = :seid')

    params = { "setid":set_id, "doe": date_of_event, "days_before":days_before-1, "days_after": days_after-1}
    if se_id is not None:
        params.update({"seid": se_id})

    cursor = conn.execute(sql, params)

    result = { 'main_data': [dict(name_en=r[1], cp_before=r[7], cp_after=r[10]) for r in cursor.fetchall()] }

    _close_db_connection(conn)

    return result

def what_is_the_effect_of_event_group_on_stock_entities(set_id, eg_id, days_before, days_after):
    conn = _get_open_db_connection(use_row_factory=False, register_udfs=True)

    sql = """
            select 	sp_starts_on.stock_entity_id,
 				e.short_name_en,

                count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_before,

                count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_before,

                count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_starts_on.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_between,

                count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_starts_on.close) * 100 < 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_between,

                count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_after,

                count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 then 1 else NULL end) * 1.0 /
                (count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 then 1 else NULL end) +
                    count(case when ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_after
            from stock_prices as sp_starts_on
            inner join stock_prices as sp_before_event
            inner JOIN stock_prices as sp_ends_on
            inner join stock_prices as sp_after_event
            inner join events AS ev
            inner join {entity} AS e
                on
                sp_starts_on.stock_entity_type_id = :setid
                and ev.event_group_id = :egid
                --and sp_starts_on.stock_entity_id IN (SELECT id from {entity} limit 10)

                and sp_starts_on.stock_entity_type_id = sp_before_event.stock_entity_type_id
                and sp_starts_on.stock_entity_id = sp_before_event.stock_entity_id
                and sp_starts_on.stock_entity_type_id = sp_after_event.stock_entity_type_id
                and sp_starts_on.stock_entity_id = sp_after_event.stock_entity_id
                and sp_starts_on.stock_entity_type_id = sp_ends_on.stock_entity_type_id
                and sp_starts_on.stock_entity_id = sp_ends_on.stock_entity_id

                and sp_starts_on.for_date > date(ev.starts_on, '-1 months')
                and ((ev.ends_on is not NULL and sp_starts_on.for_date < date(ev.ends_on, '1 months'))
                            or (ev.ends_on is NULL and sp_starts_on.for_date < date(ev.starts_on, '1 months')))

                and sp_starts_on.for_date = (select for_date from stock_prices
                                                                where for_date > date(ev.starts_on, '-1 months')
                                                                and for_date <= ev.starts_on
                                                                and stock_entity_id = sp_starts_on.stock_entity_id
                                                                and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                ORDER BY for_date DESC LIMIT 1)

                and sp_before_event.for_date = (select for_date from stock_prices
                                                                where for_date > date(ev.starts_on, '-1 months')
                                                                and	for_date < sp_starts_on.for_date
                                                                and stock_entity_id = sp_starts_on.stock_entity_id
                                                                and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                order by for_date desc limit 1 offset :days_before)

                and ((ev.ends_on is not null
                            and sp_ends_on.for_date = (select for_date from stock_prices
                                                                where for_date > date(ev.starts_on)
                                                                and for_date <= ev.ends_on
                                                                and stock_entity_id = sp_starts_on.stock_entity_id
                                                                and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                ORDER BY for_date DESC LIMIT 1))
                        OR
                         (ev.ends_on is NULL and sp_ends_on.for_date = sp_starts_on.for_date))

                and sp_after_event.for_date = (select for_date from stock_prices
                                                                where
                                                                            ((ev.ends_on is not NULL and for_date < date(ev.ends_on, '1 months'))
                                                                            or
                                                                             (ev.ends_on is NULL and for_date < date(ev.starts_on, '1 months')))
                                                                and
                                                                            ((ev.ends_on is not NULL and for_date > ev.ends_on)
                                                                             or
                                                                             (ev.ends_on is NULL and for_date > sp_starts_on.for_date))
                                                                and stock_entity_id = sp_starts_on.stock_entity_id
                                                                and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                order by for_date asc limit 1 offset :days_after)

                and sp_starts_on.stock_entity_id = e.id
                GROUP BY sp_starts_on.stock_entity_id
                ORDER BY up_prob_before desc, up_prob_after desc;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[set_id])


    params = {"setid": set_id, "egid": eg_id, "days_before": days_before - 1, "days_after": days_after - 1}

    cursor = conn.execute(sql, params)

    result_1 = [dict(id=r[0], name_en=r[1], up_prob_before=r[2], down_prob_before=r[3],
                     up_prob_between=r[4], down_prob_between=r[5],
                     up_prob_after=r[6], down_prob_after=r[7]
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

    sql = """
            select 	sp_starts_on.stock_entity_id,
 				e.short_name_en,

				sp_before_event.for_date as before_date,
				sp_before_event.close as before_close,
				((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100   cp_before,

				sp_starts_on.for_date as start_date,
				sp_starts_on.close as start_close,
				((sp_ends_on.close - sp_starts_on.close) / sp_starts_on.close) * 100 cp_between,

				sp_ends_on.for_date as end_date,
				sp_ends_on.close as end_close,
				((sp_after_event.close - sp_ends_on.close) / sp_ends_on.close) * 100 cp_after,

				sp_after_event.for_date as after_date,
				sp_after_event.close as after_close
            from stock_prices as sp_starts_on
            inner join stock_prices as sp_before_event
            inner JOIN stock_prices as sp_ends_on
            inner join stock_prices as sp_after_event
            inner join events AS ev
            inner join {entity} AS e
                    on
                    sp_starts_on.stock_entity_type_id = :setid
                    and ev.event_group_id = :egid
                    and sp_starts_on.stock_entity_id = :seid

                    and sp_starts_on.stock_entity_type_id = sp_before_event.stock_entity_type_id
                    and sp_starts_on.stock_entity_id = sp_before_event.stock_entity_id
                    and sp_starts_on.stock_entity_type_id = sp_after_event.stock_entity_type_id
                    and sp_starts_on.stock_entity_id = sp_after_event.stock_entity_id
                    and sp_starts_on.stock_entity_type_id = sp_ends_on.stock_entity_type_id
                    and sp_starts_on.stock_entity_id = sp_ends_on.stock_entity_id

                    and sp_starts_on.for_date > date(ev.starts_on, '-1 months')
                    and ((ev.ends_on is not NULL and sp_starts_on.for_date < date(ev.ends_on, '1 months'))
                                or (ev.ends_on is NULL and sp_starts_on.for_date < date(ev.starts_on, '1 months')))

                    and sp_starts_on.for_date = (select for_date from stock_prices
                                                                    where for_date > date(ev.starts_on, '-1 months')
                                                                    and for_date <= ev.starts_on
                                                                    and stock_entity_id = sp_starts_on.stock_entity_id
                                                                    and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                    ORDER BY for_date DESC LIMIT 1)

                    and sp_before_event.for_date = (select for_date from stock_prices
                                                                    where for_date > date(ev.starts_on, '-1 months')
                                                                    and	for_date < sp_starts_on.for_date
                                                                    and stock_entity_id = sp_starts_on.stock_entity_id
                                                                    and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                    order by for_date desc limit 1 offset :days_before)

                    and ((ev.ends_on is not null
                                and sp_ends_on.for_date = (select for_date from stock_prices
                                                                    where for_date > date(ev.starts_on)
                                                                    and for_date <= ev.ends_on
                                                                    and stock_entity_id = sp_starts_on.stock_entity_id
                                                                    and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                    ORDER BY for_date DESC LIMIT 1))
                            OR
                             (ev.ends_on is NULL and sp_ends_on.for_date = sp_starts_on.for_date))

                    and sp_after_event.for_date = (select for_date from stock_prices
                                                                    where
                                                                                ((ev.ends_on is not NULL and for_date < date(ev.ends_on, '1 months'))
                                                                                or
                                                                                 (ev.ends_on is NULL and for_date < date(ev.starts_on, '1 months')))
                                                                    and
                                                                                ((ev.ends_on is not NULL and for_date > ev.ends_on)
                                                                                 or
                                                                                 (ev.ends_on is NULL and for_date > sp_starts_on.for_date))
                                                                    and stock_entity_id = sp_starts_on.stock_entity_id
                                                                    and stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                                                    order by for_date asc limit 1 offset :days_after)

                    and sp_starts_on.stock_entity_id = e.id
            ORDER BY ev.starts_on;
           """.format(entity=STOCK_ENTITY_TYPE_TABLE_NAME[setid])


    params = {"setid": setid, "seid": seid, "egid": egid, "days_before": days_before - 1, "days_after": days_after - 1}

    cursor = conn.execute(sql, params)

    result_1 = [dict(id=r[0], name_en=r[1], perf_before=r[4], perf_between=r[7], perf_after=r[10], event_date=r[11]) for r in cursor.fetchall()]

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

