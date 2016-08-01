.headers ON
/*
select sp1.stock_entity_id, e.name_en, e.name_ar, e.short_name_en, e.short_name_ar,
			      sp2.for_date, sp2.close, --cp(sp2.close, sp1.close),
			      sp1.for_date, sp1.close, --cp(sp1.close, sp3.close),
			      sp3.for_date, sp3.close
            from stock_prices as sp1
            inner join stock_prices as sp2
						inner join stock_prices sp3
						inner join companies e on
                sp1.stock_entity_type_id = 1
                --and sp1.stock_entity_id = 46
                and sp1.for_date = '2015-01-22'
                and sp1.stock_entity_type_id = sp2.stock_entity_type_id
                and sp1.stock_entity_id = sp2.stock_entity_id
                and sp2.for_date = (select for_date from stock_prices where stock_entity_type_id = sp1.stock_entity_type_id
                                                and stock_entity_id = sp1.stock_entity_id and for_date < sp1.for_date
                                                order by for_date desc limit 1 offset 3)

                and sp1.stock_entity_type_id = sp3.stock_entity_type_id
                and sp1.stock_entity_id = sp3.stock_entity_id
                and sp3.for_date = (select for_date from stock_prices where stock_entity_type_id = sp1.stock_entity_type_id
                                                and stock_entity_id = sp1.stock_entity_id and for_date > sp1.for_date
                                                order by for_date asc limit 1 offset 3)
	            and sp1.stock_entity_id = e.id;

select "============================================================";

select
	sp1.for_date, e.starts_on
from stock_prices sp1
INNER JOIN events e ON
		sp1.stock_entity_type_id = 1
		AND sp1.stock_entity_id = 46
		and e.event_group_id = 2
		and sp1.for_date = (select for_date from stock_prices where stock_entity_type_id = sp1.stock_entity_type_id
												and stock_entity_id = sp1.stock_entity_id and for_date <= e.starts_on
												ORDER BY for_date DESC LIMIT 1)
		ORDER BY for_date;

select "============================================================";
*/

-- select date('2015-01-19', '-1 months');
/*
drop TABLE if EXISTS closest_dates;

CREATE TABLE closest_dates (
	se_id INT,
	for_date TEXT
);

INSERT INTO closest_dates
	select stock_entity_id, for_date
		from stock_prices sp
		where sp.stock_entity_type_id = 1
		and sp.for_date > date('2015-01-19', '-2 months')
			and sp.for_date < date('2015-01-19', '1 months')
		and for_date = (select for_date from stock_prices
										where for_date <= '2015-01-19'
											and stock_entity_id = sp.stock_entity_id
											and stock_entity_type_id = 1
											ORDER BY for_date DESC LIMIT 1);

SELECT * from closest_dates;
*/

-- EXPLAIN QUERY PLAN
/*
select 	sp1.stock_entity_id,
	-- e.name_en, e.name_ar, e.short_name_en, e.short_name_ar,
				sp2.for_date,
	--sp2.close, --cp(sp2.close, sp1.close),
				sp1.for_date,
	--sp1.close, --cp(sp1.close, sp3.close),
				sp3.for_date
	--, sp3.close
				from stock_prices as sp1
				inner join stock_prices as sp2
				inner join stock_prices sp3
				inner join companies e on
						sp1.stock_entity_type_id = 1
						and sp1.for_date > date('2015-01-19', '-2 months')
						and sp1.for_date < date('2015-01-19', '1 months')
						and sp1.for_date = (select for_date from stock_prices where for_date <= '2015-01-19'
																		and stock_entity_id = sp1.stock_entity_id
																		and stock_entity_type_id = sp1.stock_entity_type_id
																	ORDER BY for_date DESC LIMIT 1)
						and sp1.stock_entity_type_id = sp2.stock_entity_type_id
						and sp1.stock_entity_id = sp2.stock_entity_id
						and sp2.for_date = (select for_date from stock_prices where for_date < sp1.for_date
																						and stock_entity_id = sp1.stock_entity_id
																						and stock_entity_type_id = sp1.stock_entity_type_id
																						order by for_date desc limit 1 offset 3)

						and sp1.stock_entity_type_id = sp3.stock_entity_type_id
						and sp1.stock_entity_id = sp3.stock_entity_id
						and sp3.for_date = (select for_date from stock_prices where for_date > sp1.for_date
																						and stock_entity_id = sp1.stock_entity_id
																						and stock_entity_type_id = sp1.stock_entity_type_id
																						order by for_date asc limit 1 offset 3)
					and sp1.stock_entity_id = e.id
				order BY sp1.stock_entity_id;
*/

select "============================================================";

/*
select 	sp1.stock_entity_id,
	-- e.name_en, e.name_ar, e.short_name_en, e.short_name_ar,
				sp2.for_date,
	--sp2.close, --cp(sp2.close, sp1.close),
				sp1.for_date, --e.starts_on,
	--sp1.close, --cp(sp1.close, sp3.close),
				sp3.for_date
	--, count(0)
	--, sp3.close
				from stock_prices as sp1
				inner join stock_prices as sp2
				inner join stock_prices sp3
				inner JOIN events e ON
				--inner join companies e on
						e.event_group_id = 2
						and sp1.stock_entity_type_id = 1
						--and sp1.stock_entity_id IN (SELECT id from companies LIMIT 10)
 						and sp1.for_date > date(e.starts_on, '-1 months')
 						and sp1.for_date < date(e.starts_on, '1 months')

						and sp1.stock_entity_type_id = sp2.stock_entity_type_id
						and sp1.stock_entity_id = sp2.stock_entity_id
						and sp1.stock_entity_type_id = sp3.stock_entity_type_id
						and sp1.stock_entity_id = sp3.stock_entity_id

						and sp1.for_date = (select for_date from stock_prices
																	where for_date > date(e.starts_on, '-1 months')
																		and for_date <= e.starts_on
																		and stock_entity_id = sp1.stock_entity_id
																		and stock_entity_type_id = sp1.stock_entity_type_id
																	ORDER BY for_date DESC LIMIT 1)
						and sp2.for_date = (select for_date from stock_prices
																		where for_date > date(e.starts_on, '-1 months')
																		and	for_date < sp1.for_date
																		and stock_entity_id = sp1.stock_entity_id
																		and stock_entity_type_id = sp1.stock_entity_type_id
																		order by for_date desc limit 1 offset 3)
						and sp3.for_date = (select for_date from stock_prices
																		where for_date < date(e.starts_on, '1 months')
																		and for_date > sp1.for_date
																		and stock_entity_id = sp1.stock_entity_id
																		and stock_entity_type_id = sp1.stock_entity_type_id
																		order by for_date asc limit 1 offset 3)
					--and sp1.stock_entity_id = e.id
				--GROUP BY sp1.stock_entity_id
				order BY sp1.stock_entity_id;


select "============================================================";
*/

select sp1.stock_entity_id, e.name_en, --e.name_ar, e.short_name_en, e.short_name_ar,
			--sp2.for_date, sp2.close, --cp(sp2.close, sp1.close),
			--sp1.for_date, sp1.close, --cp(sp1.close, sp3.close),
			--sp3.for_date, sp3.close
			count(case when ((sp1.close - sp2.close) / sp2.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
			(count(case when ((sp1.close - sp2.close) / sp2.close) * 100 >= 0 then 1 else NULL end) +
				count(case when ((sp1.close - sp2.close) / sp2.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_before,

			count(case when ((sp1.close - sp2.close) / sp2.close) * 100 < 0 then 1 else NULL end) * 1.0 /
			(count(case when ((sp1.close - sp2.close) / sp2.close) * 100 >= 0 then 1 else NULL end) +
				count(case when ((sp1.close - sp2.close) / sp2.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_before,

			count(case when ((sp3.close - sp1.close) / sp1.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
			(count(case when ((sp3.close - sp1.close) / sp1.close) * 100 >= 0 then 1 else NULL end) +
				count(case when ((sp3.close - sp1.close) / sp1.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_after,

			count(case when ((sp3.close - sp1.close) / sp1.close) * 100 < 0 then 1 else NULL end) * 1.0 /
			(count(case when ((sp3.close - sp1.close) / sp1.close) * 100 >= 0 then 1 else NULL end) +
				count(case when ((sp3.close - sp1.close) / sp1.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_after
from stock_prices as sp1
inner join stock_prices as sp2
inner join stock_prices sp3
inner join events ev
inner join companies e on
		sp1.stock_entity_type_id = 1
		and ev.event_group_id = 2
		and sp1.stock_entity_id = 46 --IN (SELECT id from companies LIMIT 10)
		and sp1.for_date > date(ev.starts_on, '-1 months')
		and sp1.for_date < date(ev.starts_on, '1 months')

		and sp1.stock_entity_type_id = sp2.stock_entity_type_id
		and sp1.stock_entity_id = sp2.stock_entity_id
		and sp1.stock_entity_type_id = sp3.stock_entity_type_id
		and sp1.stock_entity_id = sp3.stock_entity_id

		and sp1.for_date = (select for_date from stock_prices
														where for_date > date(ev.starts_on, '-1 months')
														and for_date <= ev.starts_on
														and stock_entity_id = sp1.stock_entity_id
														and stock_entity_type_id = sp1.stock_entity_type_id
														ORDER BY for_date DESC LIMIT 1)
		and sp2.for_date = (select for_date from stock_prices
														where for_date > date(ev.starts_on, '-1 months')
														and	for_date < sp1.for_date
														and stock_entity_id = sp1.stock_entity_id
														and stock_entity_type_id = sp1.stock_entity_type_id
														order by for_date desc limit 1 offset 2)
		and sp3.for_date = (select for_date from stock_prices
														where for_date < date(ev.starts_on, '1 months')
														and for_date > sp1.for_date
														and stock_entity_id = sp1.stock_entity_id
														and stock_entity_type_id = sp1.stock_entity_type_id
														order by for_date asc limit 1 offset 2)

		and sp1.stock_entity_id = e.id
		group by sp1.stock_entity_id
		ORDER BY sp1.stock_entity_id;
