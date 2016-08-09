.timer ON
.headers ON

/*
CREATE TABLE stock_prices_jd
(
  id                     INTEGER PRIMARY KEY NOT NULL,
  stock_entity_type_id   INTEGER,
  stock_entity_id        INTEGER,
  stock_entity_argaam_id INTEGER,
  for_date               TEXT,
  year                   INTEGER,
  month                  INTEGER,
  open                   REAL,
  close                  REAL,
  min                    REAL,
  max                    REAL,
  volume                 REAL,
  amount                 REAL,
  change                 REAL,
  change_percent         REAL,
  for_date_j             INTEGER
);

INSERT INTO stock_prices_jd
  SELECT
    id,
    stock_entity_type_id,
    stock_entity_id,
    stock_entity_argaam_id,
    for_date,
    year,
    month,
    open,
    close,
    min,
    max,
    volume,
    amount,
    change,
    change_percent,
    CAST(julianday(for_date) AS INTEGER) + 1
  FROM stock_prices;

CREATE TABLE events_jd
(
    is_enabled INTEGER CHECK (0 or 1),
    created_on TEXT,
    modified_on TEXT,
    id INTEGER PRIMARY KEY NOT NULL,
    name_en TEXT,
    name_ar TEXT,
    type INTEGER,
    starts_on TEXT,
    ends_on TEXT,
    company_id INTEGER,
    event_category_id INTEGER,
    event_group_id INTEGER NOT NULL,
    created_by_id INTEGER,
    modified_by_id INTEGER,
    starts_on_j INTEGER,
    ends_on_j INTEGER,
    FOREIGN KEY (modified_by_id) REFERENCES users (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (created_by_id) REFERENCES users (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (event_group_id) REFERENCES event_groups (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (event_category_id) REFERENCES event_categories (id) DEFERRABLE INITIALLY DEFERRED,
    FOREIGN KEY (company_id) REFERENCES companies (id) DEFERRABLE INITIALLY DEFERRED
);

INSERT INTO events_jd
(id, name_en, name_ar, type, event_category_id, event_group_id, starts_on, ends_on, company_id, is_enabled,
 created_on, created_by_id, modified_on, modified_by_id, starts_on_j, ends_on_j)
  SELECT
    id,
    name_en,
    name_ar,
    type,
    event_category_id,
    event_group_id,
    starts_on,
    ends_on,
    company_id,
    is_enabled,
    created_on,
    created_by_id,
    modified_on,
    modified_by_id,
    CAST(julianday(starts_on) AS INTEGER) + 1,
    CASE
      WHEN ends_on IS NOT NULL
        THEN CAST(julianday(ends_on) AS INTEGER) + 1
      ELSE
        NULL
    END
  FROM events where id not in (select id from events_jd);
*/


/*
-- explain QUERY PLAN
SELECT
--   sp.stock_entity_type_id,
--   sp.stock_entity_id,
--   ev.event_group_id,
--   sp.for_date,
--   ev.starts_on,
--   ev.ends_on,
--   sp.for_date_j,
--   ev.starts_on_j,
--   ev.ends_on_j
  count(DISTINCT sp.for_date)
FROM stock_prices_jd sp
  INNER JOIN events_jd ev ON
                            ev.event_group_id = 2
--                             AND sp.stock_entity_id = 46
                            AND sp.stock_entity_type_id = 1

                            AND sp.for_date_j > ev.starts_on_j - 14
                            AND ((ev.ends_on is NOT null AND sp.for_date_j < ev.ends_on_j + 14)
                              OR
                                 (ev.ends_on is NULL and sp.for_date_j < ev.starts_on_j + 14));
-- ORDER BY sp.for_date;
*/

-- select * from events where event_group_id = 3;
-- select "============================================================";

/*
CREATE TEMP TABLE tt_dates
(
  for_date DATE
);
SELECT "============================================================";

-- EXPLAIN QUERY PLAN
INSERT INTO tt_dates
  SELECT
    --   sp.for_date
    --   count(sp.for_date)
    DISTINCT sp.for_date
  FROM stock_prices sp
    INNER JOIN events ev ON
                           ev.event_group_id = 2
                           AND sp.stock_entity_type_id = 1
                           AND sp.for_date > date(ev.starts_on, '-14 days')
                           AND ((ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, '14 days'))
                                OR
                                (ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, '14 days')));
SELECT "============================================================";

SELECT count(0)
FROM tt_dates;
SELECT "============================================================";
*/

-- create INDEX idx_spj_setid on stock_prices_jd (stock_entity_type_id);
-- drop INDEX idx_spj_setid;

/*
SELECT
  count(DISTINCT sp.for_date)
FROM stock_prices sp
  INNER JOIN events ev ON
                         ev.event_group_id = 2
                         AND sp.stock_entity_type_id = 1
                         AND sp.for_date > date(ev.starts_on, '-14 days')
                         AND ((ev.ends_on IS NOT NULL AND sp.for_date < date(ev.ends_on, '14 days'))
                              OR
                              (ev.ends_on IS NULL AND sp.for_date < date(ev.starts_on, '14 days')));
*/

SELECT
  count(DISTINCT sp.for_date)
FROM stock_prices_jd sp
  INNER JOIN events_jd ev ON
                         ev.event_group_id = 2
                         AND sp.stock_entity_type_id = 1
                         AND sp.for_date_j > ev.starts_on_j - 7
                         AND ((ev.ends_on IS NOT NULL AND sp.for_date_j < ev.ends_on_j + 7)
                              OR
                              (ev.ends_on IS NULL AND sp.for_date_j < ev.starts_on_j + 7));
