DROP INDEX idx_sp_dt_asc_setid_asc;
DROP INDEX idx_sp_dt_desc_setid_asc;

CREATE INDEX idx_sp_dt_asc_setid_asc on stock_prices (for_date, stock_entity_type_id);
CREATE INDEX idx_sp_dt_desc_setid_asc on stock_prices (for_date desc, stock_entity_type_id);