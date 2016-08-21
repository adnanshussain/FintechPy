.timer ON

-- .mode csv
-- .out 1.csv

-- With Nested Inner Joins
/*SELECT
  sp.stock_entity_id,
  e.name_en,
--   e.name_ar,
--   e.short_name_en,
--   e.short_name_ar,
  sp_before_start.before_dt,
  sp_before_start.before_close,
  sp_before_start.start_dt,
  sp_before_start.start_close,
  sp.for_date after_dt,
  sp.close    after_close
FROM stock_prices sp
  INNER JOIN
  (SELECT
     sp.stock_entity_id,
     sp.for_date before_dt,
     sp.close    before_close,
     --   sp_start.stock_entity_id,
     sp_start.start_dt,
     sp_start.start_close
   FROM stock_prices sp
     INNER JOIN (
                  SELECT
                    sp.stock_entity_id,
                    max(sp.for_date) start_dt,
                    sp.close         start_close
                  FROM stock_prices sp
                  WHERE
                    sp.stock_entity_type_id = 1
                    --   and sp.stock_entity_id = 46
                    AND sp.for_date = '2002-02-08'
                    OR
                    (sp.for_date > date('2002-02-08', '-1 months')
                     AND
                     sp.for_date <= '2002-02-08')
                  GROUP BY sp.stock_entity_id) sp_start
       ON
         sp.stock_entity_type_id = 1
         --   and sp.stock_entity_id = 46
         AND sp.stock_entity_id = sp_start.stock_entity_id
         AND (sp.for_date > date('2002-02-08', '-1 months')
              AND
              sp.for_date < '2002-02-08'
              AND sp.for_date = (SELECT for_date
                                 FROM stock_prices sp_inner
                                   INDEXED BY idx_sp_dt_desc_setid_asc
                                 WHERE sp_inner.stock_entity_type_id = sp.stock_entity_type_id
                                       AND sp_inner.stock_entity_id = sp.stock_entity_id
                                       AND sp_inner.for_date > date('2002-02-08', '-1 months')
                                       AND sp_inner.for_date < '2002-02-08'
                                 LIMIT 1 OFFSET 2))) sp_before_start
  INNER JOIN companies e
    ON
      sp.stock_entity_id = e.id
      and sp.stock_entity_type_id = 1
      --   and sp.stock_entity_id = 46
      AND sp.stock_entity_id = sp_before_start.stock_entity_id
      AND (sp.for_date > '2002-02-08'
           AND
           sp.for_date < date('2002-02-08', '1 months')
           AND sp.for_date = (SELECT for_date
                              FROM stock_prices sp_inner
                                INDEXED BY idx_sp_dt_asc_setid_asc
                              WHERE sp_inner.stock_entity_type_id = sp.stock_entity_type_id
                                    AND sp_inner.stock_entity_id = sp.stock_entity_id
                                    AND sp_inner.for_date > '2002-02-08'
                                    AND sp_inner.for_date < date('2002-02-08', '1 months')
                              LIMIT 1 OFFSET 2))
ORDER BY sp.stock_entity_id;*/

-- With Same Level Inner Joins (This one is Much Faster !!)
SELECT
  sp1.stock_entity_id,
  e.name_en,
  e.name_ar,
  e.short_name_en,
  e.short_name_ar,
  sp2.for_date,
  sp2.close,
--   cp(sp2.close, sp1.close),
  sp1.for_date,
  sp1.close,
--   cp(sp1.close, sp3.close),
  sp3.for_date,
  sp3.close
FROM stock_prices AS sp1
  INNER JOIN stock_prices AS sp2
  INNER JOIN stock_prices sp3
  INNER JOIN companies e ON
                           sp1.stock_entity_type_id = 1
                           --and sp1.stock_entity_id IN (SELECT id from companies LIMIT 10)
                           --{seid}
                           AND sp1.for_date > date('2002-02-08', '-1 months')
                           AND sp1.for_date <= '2002-02-08'
                           AND sp2.for_date > date('2002-02-08', '-1 months')
                           AND sp2.for_date < '2002-02-08'
                           AND sp3.for_date > '2002-02-08'
                           AND sp3.for_date <= date('2002-02-08', '1 months')

                           AND sp1.stock_entity_type_id = sp2.stock_entity_type_id
                           AND sp1.stock_entity_id = sp2.stock_entity_id
                           AND sp1.stock_entity_type_id = sp3.stock_entity_type_id
                           AND sp1.stock_entity_id = sp3.stock_entity_id

                           AND sp1.for_date = (SELECT for_date
                                               FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                               WHERE for_date > date('2002-02-08', '-1 months')
                                                     AND for_date <= '2002-02-08'
                                                     AND stock_entity_id = sp1.stock_entity_id
                                                     AND stock_entity_type_id = sp1.stock_entity_type_id
                                               LIMIT 1)
                           AND sp2.for_date = (SELECT for_date
                                               FROM stock_prices INDEXED BY idx_sp_dt_desc_setid_asc
                                               WHERE for_date > date('2002-02-08', '-1 months')
                                                     AND for_date < '2002-02-08'
                                                     AND stock_entity_id = sp1.stock_entity_id
                                                     AND stock_entity_type_id = sp1.stock_entity_type_id
                                               LIMIT 1 OFFSET 2)
                           AND sp3.for_date = (SELECT for_date
                                               FROM stock_prices INDEXED BY idx_sp_dt_asc_setid_asc
                                               WHERE for_date < date('2002-02-08', '1 months')
                                                     AND for_date > '2002-02-08'
                                                     AND stock_entity_id = sp1.stock_entity_id
                                                     AND stock_entity_type_id = sp1.stock_entity_type_id
                                               LIMIT 1 OFFSET 2)
                           AND sp1.stock_entity_id = e.id
ORDER BY sp1.stock_entity_id;
