WITH cte(rid, dt, chg, rank) AS
(
    SELECT rowid, min(for_date), change, 1
    FROM stock_prices
        WHERE
          stock_entity_type_id = 1
          AND stock_entity_id = 46

    UNION

    SELECT sp.ROWID, sp.for_date, sp.change,
      case
        WHEN sp.change >= 0 and cte.chg >= 0 then cte.rank
        when sp.change >= 0 and cte.chg < 0 then cte.rank + 1
        when sp.change < 0 and cte.chg >= 0 then cte.rank + 1
        else cte.rank
      end
    FROM stock_prices sp
      inner join cte
        ON sp.stock_entity_type_id = 1
          AND sp.stock_entity_id = 46
          AND sp.ROWID = cte.rid + 1
),
source_cte as
(
SELECT dt, chg, max(rank) rank
FROM cte
  GROUP BY dt, chg
)
select
  min(dt), max(dt), count(*),
  case
    when chg >= 0 then 'Rally'
    else 'Decline'
  end
from source_cte
GROUP BY rank
ORDER BY count(*) desc;