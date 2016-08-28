.mode csv
-- .headers on

-- .out events_jd.csv
-- select id, event_group_id, starts_on, ends_on, starts_on_j, ends_on_j from events_jd;

.out all_stock_prices.csv
select stock_entity_type_id, stock_entity_id, for_date, close as closing_price, change, change_percent from stock_prices;