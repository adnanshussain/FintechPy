.header ON
.timer ON
-- .stats ON
.nullvalue NULL

select ep.id, sp.stock_entity_id, sp.for_date, sp.close
from
(
  select e.id, sp.stock_entity_id, max(for_date) as best_for_date
  from events e
  join stock_prices sp on (e.ends_on is null and sp.for_date <= e.starts_on)
                or (e.ends_on is not null and sp.for_date between e.starts_on and e.ends_on)
    WHERE
  e.event_group_id = 4
  AND sp.stock_entity_type_id = 1
  --AND sp.stock_entity_id = 46
  group by e.id, sp.stock_entity_id
) ep
join stock_prices sp on sp.stock_entity_id = ep.stock_entity_id
                        and sp.for_date = ep.best_for_date;
.exit

/*
select
  ev.starts_on, sp.for_date, sp.close
  --count(0)
from stock_prices_jd sp
INNER JOIN events_jd ev
WHERE
  ev.event_group_id = 2
  and sp.stock_entity_type_id = 1
  and sp.stock_entity_id = 46
  and (sp.for_date = ev.starts_on)
  ORDER BY ev.starts_on;

.exit
  or
  sp.for_date = (select for_date FROM stock_prices_jd
                  WHERE for_date < ev.starts_on
                    and for_date > date(ev.starts_on, '-14 days')
                  and stock_entity_type_id = sp.stock_entity_type_id
                  and stock_entity_id = sp.stock_entity_id
                  ORDER BY for_date_j DESC
                  LIMIT 1))

  ;

.exit
*/

-- .mode csv
-- .out sp_all.csv

with cte(id, dt) AS (
  SELECT id, starts_on dt FROM events_jd WHERE event_group_id = 4
  UNION
  SELECT id, CASE WHEN ends_on IS NULL THEN starts_on ELSE ends_on END dt FROM events_jd WHERE event_group_id = 4
), cte2 as (
SELECT
  cte.*,
  sp.stock_entity_id,
  sp.for_date,
  sp.close
FROM cte, stock_prices_jd sp
WHERE
  sp.stock_entity_type_id = 1
  AND sp.stock_entity_id IN (46)
  AND sp.for_date BETWEEN '2002-02-07' AND '2002-02-10'
)
-- select * from cte2;
-- .exit
select
  *
from cte2 t1, cte2 t2
where
  t1.id = t2.id
  and t1.for_date < t2.dt
  and t1.for_date < t2.for_date;



/*
with cte(eid, dt) as (
  select id, date(starts_on, '-14 days') from events_jd where event_group_id = 4
  union all
  select eid, date(dt, '1 days') from cte where dt < (select date(starts_on, '14 days') from events_jd where id =  eid)
)
select
  dt2.dt, sp.stock_entity_type_id, sp.stock_entity_id, sp.for_date, sp.close
from (select DISTINCT dt from cte ORDER BY dt) dt2, stock_prices_jd sp
WHERE
  sp.stock_entity_type_id = 1
  AND sp.stock_entity_id = 46
  and sp.for_date BETWEEN '2002-01-20' and '2002-03-20'
  and dt is not NULL
  AND sp.stock_entity_id is not NULL;
*/

.exit

CREATE TEMP TABLE tt_sp AS
  SELECT
    ev.id evid,
    ev.event_group_id,
    ev.starts_on,
    ev.ends_on,
    sp.stock_entity_type_id,
    sp.stock_entity_id,
    sp.for_date,
    sp.for_date_j,
    sp.close,
    sp.change_percent
  FROM events_jd ev
    inner JOIN stock_prices_jd sp ON
                              ev.event_group_id = 4
                              AND sp.stock_entity_type_id = 1
                              AND sp.for_date_j > ev.starts_on_j - 7 -- date(ev.starts_on, '-14 days')
                              AND ((ev.ends_on IS NOT NULL AND sp.for_date_j < ev.ends_on_j + 7) --date(ev.ends_on, '14 days'))
                                   OR
                                   (ev.ends_on IS NULL AND sp.for_date_j < ev.starts_on_j + 7)) --date(ev.starts_on, '14 days')))
  ORDER BY ev.starts_on_j, sp.stock_entity_type_id, stock_entity_id, sp.for_date_j;

-- .mode csv
-- .out sp_all.csv
--
-- select rowid, * from tt_sp;
-- .exit

SELECT
  sp_start.*
FROM tt_sp sp
  INNER JOIN tt_sp sp_start
    ON
      sp.stock_entity_id = sp_start.stock_entity_id
      AND (sp_start.for_date = ev.starts_on OR sp_start.rowid =

.out sp_real.csv

SELECT
  sp_start.*
FROM stock_prices_jd sp_start
  INNER JOIN events_jd ev
    ON
      ev.event_group_id = 2
        and sp_start.stock_entity_id = 46
      AND sp_start.for_date_j = ev.starts_on_j;