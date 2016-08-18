.header ON
.timer ON
-- .stats ON
.nullvalue NULL

.mode csv
.out all.csv

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
        ev.event_group_id = 3
        AND sp.stock_entity_type_id = 1
        AND sp.stock_entity_id in (46)
        AND sp.for_date > date(ev.starts_on, '-1 months')
        AND ((ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, '1 months'))
             OR (ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, '1 months')));

create index tt_idx_sp_dt_desc_seid on tt_sp (for_date DESC, stock_entity_id);
create index tt_idx_sp_dt_asc_seid on tt_sp (for_date ASC, stock_entity_id);

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
        AND sp.for_date > date(ev.starts_on, '-1 months')
        AND sp.for_date < ev.starts_on
        AND sp.for_date = (SELECT for_date
                                  FROM tt_sp INDEXED BY tt_idx_sp_dt_desc_seid
                                  WHERE stock_entity_id = sp.stock_entity_id
                                        AND for_date > date(ev.starts_on, '-1 months')
                                        AND for_date < ev.starts_on
                                  LIMIT 1 OFFSET 2);

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
        and sp.for_date > date(ev.starts_on, '-1 months')
        AND sp.for_date <= ev.starts_on
  GROUP BY ev.id, ev.type, ev.starts_on, ev.ends_on, sp.stock_entity_id;

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
        ((ev.ends_on IS NULL AND sp.for_date > date(ev.starts_on, '-1 months') AND sp.for_date <= ev.starts_on)
         OR
         (ev.ends_on IS NOT NULL AND sp.for_date > ev.starts_on AND sp.for_date <= ev.ends_on))
  GROUP BY ev.id, ev.type, ev.starts_on, ev.ends_on, sp.stock_entity_id;

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
        ((ev.ends_on IS NULL AND sp.for_date > ev.starts_on AND sp.for_date < date(ev.starts_on, '1 months'))
          OR (ev.ends_on IS NOT NULL AND sp.for_date > ev.ends_on AND sp.for_date < date(ev.ends_on, '1 months')))
         AND sp.for_date =
             (SELECT sp_inner.for_date
              FROM tt_sp sp_inner INDEXED BY tt_idx_sp_dt_asc_seid
              WHERE
                    sp_inner.stock_entity_id = sp.stock_entity_id
                    AND
                    ((ev.ends_on IS NULL AND sp_inner.for_date > ev.starts_on AND sp_inner.for_date < date(ev.starts_on, '1 months'))
                    OR
                     (ev.ends_on IS NOT NULL AND sp_inner.for_date > ev.ends_on AND sp_inner.for_date < date(ev.ends_on, '1 months')))
              LIMIT 1 OFFSET 2);

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
  INNER JOIN companies e
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

select * from tt_source;

/*select
        stock_entity_id,
 				short_name_en,

        count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end)) * 100                            up_prob_before,

        count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((start_close - before_close) / before_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((start_close - before_close) / before_close) * 100 < 0 then 1 else NULL end)) * 100                            down_prob_before,

        count(case when ((end_close - start_close) / start_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((end_close - start_close) / end_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((end_close - start_close) / end_close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_between,

        count(case when ((end_close - start_close) / start_close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((end_close - start_close) / end_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((end_close - start_close) / end_close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_between,

        count(case when ((after_close - end_close) / after_close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((after_close - end_close) / after_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((after_close - end_close) / after_close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_after,

        count(case when ((after_close - end_close) / after_close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((after_close - end_close) / after_close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((after_close - end_close) / after_close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_after
from tt_source
GROUP BY stock_entity_id
ORDER BY up_prob_before desc, up_prob_after desc;*/


-- SOLVED
SELECT
  sp_evs.stock_entity_id,
  e.short_name_en,

  sp_bev.for_date         AS                                   before_date,
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
  INNER JOIN companies AS e
    ON
      sp_evs.stock_entity_type_id = 1
      AND ev.event_group_id = 3
      AND sp_evs.stock_entity_id = 46

      and sp_bev.for_date > date(ev.starts_on, '-1 months')
      and sp_bev.for_date < ev.starts_on
      and sp_evs.for_date > date(ev.starts_on, '-1 months')
      and sp_evs.for_date <= ev.starts_on
      and ((ev.ends_on is NULL and sp_eve.for_date > date(ev.starts_on, '-1 months') and sp_evs.for_date <= ev.starts_on)
        OR
           (ev.ends_on is not NULL and sp_eve.for_date > ev.starts_on and sp_evs.for_date <= ev.ends_on))
      and ((ev.ends_on is NULL and sp_aev.for_date > ev.starts_on and sp_evs.for_date < date(ev.starts_on, '1 months'))
        OR
           (ev.ends_on is not NULL and sp_aev.for_date > ev.ends_on and sp_evs.for_date < date(ev.ends_on, '1 months')))

      AND sp_evs.stock_entity_type_id = sp_bev.stock_entity_type_id
      AND sp_evs.stock_entity_id = sp_bev.stock_entity_id
      AND sp_evs.stock_entity_type_id = sp_aev.stock_entity_type_id
      AND sp_evs.stock_entity_id = sp_aev.stock_entity_id
      AND sp_evs.stock_entity_type_id = sp_eve.stock_entity_type_id
      AND sp_evs.stock_entity_id = sp_eve.stock_entity_id

      AND sp_evs.for_date = (SELECT for_date
                                   FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                   WHERE for_date > DATE(ev.starts_on, '-1 months')
                                         AND for_date <= ev.starts_on
                                         AND stock_entity_id = sp_evs.stock_entity_id
                                         AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                   LIMIT 1)

      AND sp_bev.for_date = (SELECT for_date
                                      FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                      WHERE for_date > DATE(ev.starts_on, '-1 months')
                                            AND for_date < ev.starts_on
                                            AND stock_entity_id = sp_evs.stock_entity_id
                                            AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                      LIMIT 1 OFFSET 2)

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
                                       ((ev.ends_on IS NOT NULL AND for_date < DATE(ev.ends_on, '1 months'))
                                        OR
                                        (ev.ends_on IS NULL AND for_date < DATE(ev.starts_on, '1 months')))
                                       AND
                                       ((ev.ends_on IS NOT NULL AND for_date > ev.ends_on)
                                        OR
                                        (ev.ends_on IS NULL AND for_date > ev.starts_on))
                                       AND stock_entity_id = sp_evs.stock_entity_id
                                       AND stock_entity_type_id = sp_evs.stock_entity_type_id
                                     LIMIT 1 OFFSET 2)

      AND sp_evs.stock_entity_id = e.id
ORDER BY ev.starts_on;



-- .out all.csv

      /*select 	sp_evs.stock_entity_id,
 				e.short_name_en,

        count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 < 0 then 1 else NULL end)) * 100                            up_prob_before,

        count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_evs.close - sp_bev.close) / sp_bev.close) * 100 < 0 then 1 else NULL end)) * 100                            down_prob_before,

        count(case when ((sp_eve.close - sp_evs.close) / sp_evs.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_eve.close - sp_evs.close) / sp_eve.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_eve.close - sp_evs.close) / sp_eve.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_between,

        count(case when ((sp_eve.close - sp_evs.close) / sp_evs.close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_eve.close - sp_evs.close) / sp_eve.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_eve.close - sp_evs.close) / sp_eve.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_between,

        count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 >= 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 < 0 then 1 else NULL end)) * 100 up_prob_after,

        count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 < 0 then 1 else NULL end) * 1.0 /
        (count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 >= 0 then 1 else NULL end) +
         count(case when ((sp_aev.close - sp_eve.close) / sp_aev.close) * 100 < 0 then 1 else NULL end)) * 100 down_prob_after
            from stock_prices as sp_evs
            inner join stock_prices as sp_bev
            inner JOIN stock_prices as sp_eve
            inner join stock_prices as sp_aev
            inner join events AS ev
            inner join companies AS e
                on
                sp_evs.stock_entity_type_id = 1
                and ev.event_group_id = 3
                and sp_evs.stock_entity_id = 46

                and sp_bev.for_date > date(ev.starts_on, '-1 months')
                and sp_bev.for_date < ev.starts_on
                and sp_evs.for_date > date(ev.starts_on, '-1 months')
                and sp_evs.for_date <= ev.starts_on
                and ((ev.ends_on is NULL and sp_eve.for_date > date(ev.starts_on, '-1 months') and sp_evs.for_date <= ev.starts_on)
                  OR
                     (ev.ends_on is not NULL and sp_eve.for_date > ev.starts_on and sp_evs.for_date <= ev.ends_on))
                and ((ev.ends_on is NULL and sp_aev.for_date > ev.starts_on and sp_evs.for_date < date(ev.starts_on, '1 months'))
                  OR
                     (ev.ends_on is not NULL and sp_aev.for_date > ev.ends_on and sp_evs.for_date < date(ev.ends_on, '1 months')))

                and sp_bev.stock_entity_id = sp_evs.stock_entity_id
                and sp_bev.stock_entity_type_id = sp_evs.stock_entity_type_id
                and sp_eve.stock_entity_id = sp_evs.stock_entity_id
                and sp_eve.stock_entity_type_id = sp_evs.stock_entity_type_id
                and sp_aev.stock_entity_id = sp_aev.stock_entity_id
                and sp_aev.stock_entity_type_id = sp_evs.stock_entity_type_id

                and sp_evs.for_date = (select for_date from stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                                                where for_date > date(ev.starts_on, '-1 months')
                                                                and for_date <= ev.starts_on
                                                                and stock_entity_id = sp_evs.stock_entity_id
                                                                and stock_entity_type_id = sp_evs.stock_entity_type_id
                                                                LIMIT 1)

                and sp_bev.for_date = (select for_date from stock_prices  INDEXED BY idx_sp_dt_desc_setid_asc
                                                                where for_date > date(ev.starts_on, '-1 months')
                                                                and	for_date < sp_evs.for_date
                                                                and stock_entity_id = sp_evs.stock_entity_id
                                                                and stock_entity_type_id = sp_evs.stock_entity_type_id
                                                                limit 1 offset 2)

                and ((ev.ends_on is not null
                            and sp_eve.for_date = (select for_date from stock_prices  INDEXED BY idx_sp_dt_desc_setid_asc
                                                                where for_date > date(ev.starts_on)
                                                                and for_date <= ev.ends_on
                                                                and stock_entity_id = sp_evs.stock_entity_id
                                                                and stock_entity_type_id = sp_evs.stock_entity_type_id
                                                                LIMIT 1))
                        OR
                         (ev.ends_on is NULL and sp_eve.for_date = sp_evs.for_date))

                and sp_aev.for_date = (select for_date from stock_prices  INDEXED BY idx_sp_dt_asc_setid_asc
                                                                where
                                                                            ((ev.ends_on is not NULL and for_date < date(ev.ends_on, '1 months'))
                                                                            or
                                                                             (ev.ends_on is NULL and for_date < date(ev.starts_on, '1 months')))
                                                                and
                                                                            ((ev.ends_on is not NULL and for_date > ev.ends_on)
                                                                             or
                                                                             (ev.ends_on is NULL and for_date > sp_evs.for_date))
                                                                and stock_entity_id = sp_evs.stock_entity_id
                                                                and stock_entity_type_id = sp_evs.stock_entity_type_id
                                                                limit 1 offset 2)

                and sp_evs.stock_entity_id = e.id
                GROUP BY sp_evs.stock_entity_id
                ORDER BY up_prob_before desc, up_prob_after desc;*/