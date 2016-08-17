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
        ev.event_group_id = 2
        AND sp.stock_entity_type_id = 1
        --AND sp.stock_entity_id in (46)
        AND sp.for_date > date(ev.starts_on, '-14 days')
        AND ((ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, '14 days'))
             OR (ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, '14 days')));

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
        AND sp.for_date > date(ev.starts_on, '-14 days')
        AND sp.for_date < ev.starts_on
        AND sp.for_date = (SELECT for_date
                                  FROM tt_sp INDEXED BY tt_idx_sp_dt_desc_seid
                                  WHERE stock_entity_id = sp.stock_entity_id
                                        AND for_date > date(ev.starts_on, '-14 days')
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
        and sp.for_date > date(ev.starts_on, '-14 days')
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
        ((ev.ends_on IS NULL AND sp.for_date > date(ev.starts_on, '-14 days') AND sp.for_date <= ev.starts_on)
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
        ((ev.ends_on IS NULL AND sp.for_date > ev.starts_on AND sp.for_date < date(ev.starts_on, '14 days'))
          OR (ev.ends_on IS NOT NULL AND sp.for_date > ev.ends_on AND sp.for_date < date(ev.ends_on, '14 days')))
         AND sp.for_date =
             (SELECT sp_inner.for_date
              FROM tt_sp sp_inner INDEXED BY tt_idx_sp_dt_asc_seid
              WHERE
                    sp_inner.stock_entity_id = sp.stock_entity_id
                    AND
                    ((ev.ends_on IS NULL AND sp_inner.for_date > ev.starts_on AND sp_inner.for_date < date(ev.starts_on, '14 days'))
                    OR
                     (ev.ends_on IS NOT NULL AND sp_inner.for_date > ev.ends_on AND sp_inner.for_date < date(ev.ends_on, '14 days')))
              LIMIT 1 OFFSET 2);

SELECT
  ae.event_id,
  ae.stock_entity_id,
  ae.starts_on,
  ae.ends_on,
  be_se_ee.before_dt,
  be_se_ee.before_close,
  be_se_ee.start_date,
  be_se_ee.start_close,
  be_se_ee.end_date  end_date,
  be_se_ee.end_close end_close,
  ae.for_date        after_date,
  ae.close           after_close
FROM tt_sp_after_ev ae
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
      ae.event_id = be_se_ee.event_id
      AND ae.stock_entity_id = be_se_ee.stock_entity_id;

.exit

/*
SELECT
    sp_starts_on.stock_entity_id,
    e.short_name_en,
    count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 up_prob_before,

    count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 down_prob_before,

    count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_starts_on.close) * 100 >= 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 up_prob_between,

    count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_starts_on.close) * 100 < 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_ends_on.close - sp_starts_on.close) / sp_ends_on.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 down_prob_between,

    count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 up_prob_after,

    count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 THEN 1 ELSE NULL END) * 1.0 /
    (count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 >= 0 THEN 1 ELSE NULL END) +
     count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 down_prob_after
*/