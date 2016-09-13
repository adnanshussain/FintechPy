import sqlite3
import webapp.data_access as da

def get_and_apply_splits():
    with da._get_open_db_connection() as conn:
        sql = """
            select company_id, split_date, ratio from tc_splits
            order by company_id, split_date asc;
            """

        cursor = conn.execute(sql)

        for split in cursor:
            sql_2 = """
                update tc_company_stock_prices set
                  open = open / {2},
                  max = max / {2},
                  min = min / {2},
                  close = close / {2},
                  volume = volume * {2},
                  split_count = split_count + 1
                where company_id = {0}
                and  for_date < '{1}';
            """.format(split['company_id'], split['split_date'], split['ratio'])

            print(sql_2)

            cursor_2 = conn.execute(sql_2)
            print('Applied split for {0}, records affected {1}'.format(split['company_id'], cursor_2.rowcount))

# get_and_apply_splits()

