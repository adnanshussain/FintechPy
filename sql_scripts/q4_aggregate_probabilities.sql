.header ON
.timer ON
-- .stats ON
.nullvalue NULL

CREATE TEMP TABLE tt_dates_desc
(
  for_date   DATE,
  for_date_j INTEGER
);

CREATE TEMP TABLE tt_dates_asc
(
  for_date   DATE,
  for_date_j INTEGER
);

-- EXPLAIN QUERY PLAN
INSERT INTO tt_dates_desc
  SELECT DISTINCT
    sp.for_date,
    sp.for_date_j
  FROM stock_prices_jd sp
    INNER JOIN events_jd ev ON
                              ev.event_group_id = 4
                              AND sp.stock_entity_type_id = 1
                              AND sp.for_date > date(ev.starts_on, '-9 days')
                              AND ((ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, '7 days'))
                                   OR
                                   (ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, '7 days')))
  ORDER BY for_date DESC;

INSERT INTO tt_dates_asc
  SELECT
    for_date,
    for_date_j
  FROM tt_dates_desc
  ORDER BY for_date;

--SELECT count(0) from tt_dates_desc limit 100;

CREATE TEMP TABLE tt_stock_prices_jd AS
  SELECT *
  FROM stock_prices_jd
  WHERE stock_entity_type_id = 1
        AND for_date IN (SELECT for_date
                         FROM tt_dates_desc);

-- CREATE INDEX tt_idx_sp_setid ON tt_stock_prices_jd (stock_entity_type_id);

--select count(0) from tt_stock_prices_jd ORDER BY for_date LIMIT 100;

CREATE TEMP TABLE tt_sp_before AS
  SELECT
    sp.stock_entity_id,
    ev.id event_id,
    sp.for_date,
    sp.close
  FROM tt_stock_prices_jd sp
    INNER JOIN events_jd ev
      ON
        sp.stock_entity_type_id = 1
        AND ev.event_group_id = 4
        AND sp.for_date_j = (SELECT for_date_j
                             FROM tt_dates_desc
                             WHERE for_date_j < ev.starts_on_j
                                   AND for_date_j > ev.starts_on_j - 14
                             LIMIT 1
                             OFFSET 2);

CREATE TEMP TABLE tt_sp_start AS
  SELECT
    sp.stock_entity_id,
    ev.id event_id,
    sp.for_date,
    sp.close
  FROM tt_stock_prices_jd sp
    INNER JOIN events_jd ev
      ON
        sp.stock_entity_type_id = 1
        AND ev.event_group_id = 4
        AND sp.for_date_j = (SELECT for_date_j
                             FROM tt_dates_desc
                             WHERE for_date_j <= ev.starts_on_j
                                   AND for_date_j > ev.starts_on_j - 14
                             LIMIT 1);

CREATE TEMP TABLE tt_sp_end_1 AS
  SELECT
    sp.stock_entity_id,
    ev.id event_id,
    sp.for_date,
    sp.close
  FROM tt_stock_prices_jd sp
    INNER JOIN events_jd ev
      ON
        sp.stock_entity_type_id = 1
        AND ev.event_group_id = 4
        AND ((ev.ends_on IS NOT NULL AND sp.for_date_j = (SELECT for_date_j
                                                         FROM tt_dates_desc
                                                         WHERE for_date_j <= ev.ends_on_j
                                                               AND for_date_j > ev.starts_on_j
                                                         LIMIT 1))
          /*OR
             (ev.ends_on IS NULL AND sp.for_date_j = (SELECT for_date_j
                                                         FROM tt_dates_desc
                                                         WHERE for_date_j <= ev.starts_on_j
                                                               AND for_date_j > ev.starts_on_j - 14
                                                         LIMIT 1))*/);

CREATE TEMP TABLE tt_sp_end_2 AS
  SELECT
    sp.stock_entity_id,
    ev.id event_id,
    sp.for_date,
    sp.close
  FROM tt_stock_prices_jd sp
    INNER JOIN events_jd ev
      ON
        sp.stock_entity_type_id = 1
        AND ev.event_group_id = 4
        AND (ev.ends_on IS NULL AND sp.for_date_j = (SELECT for_date_j
                                                         FROM tt_dates_desc
                                                         WHERE for_date_j <= ev.starts_on_j
                                                            AND for_date_j > ev.starts_on_j - 14
                                                         LIMIT 1));

SELECT count(0) FROM tt_sp_before;
SELECT count(0) FROM tt_sp_start;
SELECT count(0) FROM tt_sp_end_1;
SELECT count(0) FROM tt_sp_end_2;

.exit

SELECT
  /*sp_before.stock_entity_id,
  sp_before.for_date,
  sp_before.close,
  sp_start.for_date,
  sp_start.close*/
  sp_start.stock_entity_id,
  count(0)
FROM tt_sp_before sp_before
  INNER JOIN tt_sp_start sp_start
  INNER JOIN tt_sp_end sp_end
    ON
      sp_before.stock_entity_id = sp_start.stock_entity_id
      AND sp_before.event_id = sp_start.event_id
      AND sp_end.stock_entity_id = sp_start.stock_entity_id
      AND sp_end.event_id = sp_start.event_id
GROUP BY sp_start.stock_entity_id
ORDER BY count(0) DESC, sp_start.stock_entity_id DESC
LIMIT 10;


/*
SELECT
    sp_starts_on.stock_entity_id seid,
    ev.id eid,
    sp_before_event.for_date before_dt,
    sp_before_event.close before_close
--   count(*)
FROM
  tt_stock_prices_jd AS sp_starts_on
  INNER JOIN tt_stock_prices_jd AS sp_before_event
--   INNER JOIN tt_stock_prices_jd AS sp_ends_on
--   INNER JOIN tt_stock_prices_jd AS sp_after_event
  INNER JOIN events_jd AS ev
  INNER JOIN companies AS e
    ON
      sp_starts_on.stock_entity_type_id = 1
      AND ev.event_group_id = 2
--       and sp_starts_on.stock_entity_id = 46
      AND sp_starts_on.stock_entity_id = e.id

      AND sp_starts_on.stock_entity_type_id = sp_before_event.stock_entity_type_id
      AND sp_starts_on.stock_entity_id = sp_before_event.stock_entity_id

--       AND sp_starts_on.stock_entity_type_id = sp_after_event.stock_entity_type_id
--       AND sp_starts_on.stock_entity_id = sp_after_event.stock_entity_id
--       AND sp_starts_on.stock_entity_type_id = sp_ends_on.stock_entity_type_id
--       AND sp_starts_on.stock_entity_id = sp_ends_on.stock_entity_id

      and sp_starts_on.for_date_j = (select for_date_j FROM tt_dates_desc
                                    WHERE for_date_j <= ev.starts_on_j
                                    LIMIT 1)

      and sp_before_event.for_date_j = (select for_date_j FROM tt_dates_desc
                                        WHERE for_date_j < sp_starts_on.for_date_j
                                        LIMIT 1 OFFSET 2)

--       and sp_after_event.for_date = (select for_date FROM tt_dates_asc
--                                       WHERE for_date > ev.starts_on
--                                       LIMIT 1 OFFSET 2)
;
*/


/*
SELECT
    sp_starts_on.stock_entity_id,
    e.short_name_en,



    */
/*count(CASE WHEN ((sp_starts_on.close - sp_before_event.close) / sp_before_event.close) * 100 >= 0 THEN 1 ELSE NULL END) * 1.0 /
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
     count(CASE WHEN ((sp_after_event.close - sp_ends_on.close) / sp_after_event.close) * 100 < 0 THEN 1 ELSE NULL END)) * 100 down_prob_after*//*


    sp_before_event.for_date,
    sp_starts_on.for_date,
    --sp_ends_on.for_date,
    sp_after_event.for_date

FROM tt_stock_prices_jd AS sp_starts_on
  INNER JOIN tt_stock_prices_jd AS sp_before_event
  --INNER JOIN tt_stock_prices_jd AS sp_ends_on
  INNER JOIN tt_stock_prices_jd AS sp_after_event
  INNER JOIN events_jd AS ev
  INNER JOIN companies AS e
    ON
      sp_starts_on.stock_entity_type_id = 1
      AND ev.event_group_id = 4
      and sp_starts_on.stock_entity_id = 46

      AND sp_starts_on.stock_entity_type_id = sp_before_event.stock_entity_type_id
      AND sp_starts_on.stock_entity_id = sp_before_event.stock_entity_id
      AND sp_starts_on.stock_entity_type_id = sp_after_event.stock_entity_type_id
      AND sp_starts_on.stock_entity_id = sp_after_event.stock_entity_id
--       AND sp_starts_on.stock_entity_type_id = sp_ends_on.stock_entity_type_id
--       AND sp_starts_on.stock_entity_id = sp_ends_on.stock_entity_id

      AND sp_starts_on.for_date_j > ev.starts_on_j - 14
      AND ((ev.ends_on IS NOT NULL AND sp_starts_on.for_date_j < ev.ends_on_j + 14)
           OR (ev.ends_on IS NULL AND sp_starts_on.for_date_j < ev.starts_on_j + 14))

      AND sp_starts_on.for_date_j = (SELECT for_date_j
                                      FROM tt_dates
                                      WHERE for_date_j > ev.starts_on_j - 14
                                         AND for_date_j <= ev.starts_on_j
--                                          AND stock_entity_id = sp_starts_on.stock_entity_id
--                                          AND stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                      ORDER BY for_date_j DESC LIMIT 1)

      AND sp_before_event.for_date_j = (SELECT for_date_j
                                        FROM tt_dates
                                        WHERE for_date_j > ev.starts_on_j - 14
                                            AND for_date_j < sp_starts_on.for_date_j
--                                             AND stock_entity_id = sp_starts_on.stock_entity_id
--                                             AND stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                        ORDER BY for_date_j DESC LIMIT 1 OFFSET 2)


*/
/*
      AND ((ev.ends_on IS NOT NULL
            AND sp_ends_on.for_date_j = (SELECT for_date_j
                                       FROM tt_dates
                                       WHERE for_date_j > ev.starts_on_j
                                             AND for_date_j <= ev.ends_on_j
--                                              AND stock_entity_id = sp_starts_on.stock_entity_id
--                                              AND stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                       ORDER BY for_date_j
                                         DESC
                                       LIMIT 1))
           OR
           (ev.ends_on IS NULL AND sp_ends_on.for_date_j = sp_starts_on.for_date_j))
*//*



      AND sp_after_event.for_date   = (SELECT for_date_j
                                        FROM tt_dates
                                        WHERE
                                          ((ev.ends_on IS NOT NULL AND for_date_j < ev.ends_on_j + 14)
                                            OR
                                          (ev.ends_on IS NULL AND for_date_j < ev.starts_on_j + 14))
                                          AND
                                          ((ev.ends_on IS NOT NULL AND for_date_j > ev.ends_on_j)
                                            OR
                                          (ev.ends_on IS NULL AND for_date_j > ev.starts_on_j))
--                                         AND stock_entity_id = sp_starts_on.stock_entity_id
--                                         AND stock_entity_type_id = sp_starts_on.stock_entity_type_id
                                      ORDER BY for_date_j ASC LIMIT 1 OFFSET 2)

      AND sp_starts_on.stock_entity_id = e.id;
*/
-- GROUP BY sp_starts_on.stock_entity_id
-- ORDER BY up_prob_before DESC, up_prob_after DESC;
