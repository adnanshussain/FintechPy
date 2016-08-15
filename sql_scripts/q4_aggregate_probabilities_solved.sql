.header ON
.timer ON
-- .stats ON
.nullvalue NULL

select
  *
from events ev
INNER JOIN stock_prices sp ON

  sp.for_date