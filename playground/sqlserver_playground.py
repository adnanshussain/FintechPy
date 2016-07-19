import pypyodbc

sql_server_conn_str = 'Driver={SQL Server Native Client 11.0};Server=172.16.3.65;Database=ArgaamPlus;Uid=argaamplususer;Pwd=argplus123$;'
# sql_server_conn_str = 'Driver={SQL Server Native Client 11.0};Server=172.16.3.51;Database=argaam_analytics;Uid=argplus_user;Pwd=argplus123$;'

conn = pypyodbc.connect(sql_server_conn_str)

cur = conn.cursor()
# cur.execute("{call dbo.SP_Q1_StockEntityWasUpOrDownByPercent(?,?,?,?,?,?)}", (77, 1, 'up', 5, 2001, 2005))

cur.execute("select * from companystockpricesarchive where companyid = ?", (77,))

# for d in cur.description:
#     print(d)

print("")

for r in cur.fetchall():
    print(r)