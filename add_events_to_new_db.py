import sqlite3, datetime
from webapp.config import NEW_DB_PATH

def do_work():
    conn = sqlite3.connect(NEW_DB_PATH)
    cursor = conn.cursor()

    event_cat_id = cursor.execute("select id from event_categories where name_en = ?", ('Earning Announcements',)).fetchone()[0]
    print(event_cat_id)
    company_id = cursor.execute("select id, name_en from companies where argaam_id = ?", (77,)).fetchone()[0]
    print(company_id)
    cursor.close()

    cursor = conn.cursor()
    cursor.executemany("INSERT INTO events(is_enabled, created_on, name_en, type, starts_on, company_id, event_category_id)\
                   VALUES (?,?,?,?,?,?,?);",
                       [
                        (True, datetime.datetime.now(), 'Sabic Q1-2005', 1, datetime.date(2005,4,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2005', 1, datetime.date(2005,7,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2005', 1, datetime.date(2005,10,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2005', 1, datetime.date(2006,1,22), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2006', 1, datetime.date(2006,4,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2006', 1, datetime.date(2006,7,16), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2006', 1, datetime.date(2006,10,15), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2006', 1, datetime.date(2007,1,21), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2007', 1, datetime.date(2007,4,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2007', 1, datetime.date(2007,7,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2007', 1, datetime.date(2007,10,22), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2007', 1, datetime.date(2008,1,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2008', 1, datetime.date(2008,4,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2008', 1, datetime.date(2008,7,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2008', 1, datetime.date(2008,10,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2008', 1, datetime.date(2009,1,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2009', 1, datetime.date(2009,4,20), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2009', 1, datetime.date(2009,7,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2009', 1, datetime.date(2009,10,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2009', 1, datetime.date(2010,1,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2010', 1, datetime.date(2010,4,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2010', 1, datetime.date(2010,7,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2010', 1, datetime.date(2010,10,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2010', 1, datetime.date(2011,1,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2011', 1, datetime.date(2011,4,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2011', 1, datetime.date(2011,7,16), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2011', 1, datetime.date(2011,10,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2011', 1, datetime.date(2012,1,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2012', 1, datetime.date(2012,4,16), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2012', 1, datetime.date(2012,7,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2012', 1, datetime.date(2012,10,16), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2012', 1, datetime.date(2013,1,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2013', 1, datetime.date(2013,4,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2013', 1, datetime.date(2013,7,20), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2013', 1, datetime.date(2013,10,26), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2013', 1, datetime.date(2014,1,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2014', 1, datetime.date(2014,4,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2014', 1, datetime.date(2014,7,19), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2014', 1, datetime.date(2014,10,25), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2014', 1, datetime.date(2015,1,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2015', 1, datetime.date(2015,4,18), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2015', 1, datetime.date(2015,7,25), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2015', 1, datetime.date(2015,10,17), company_id, event_cat_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2015', 1, datetime.date(2016,1,16), company_id, event_cat_id),
                        ])
    conn.commit()
    conn.close()
