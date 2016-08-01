# THE REASON THIS FILE IS IN THE ROOT FOLDER IS BECUASE I NEED TO RUN IT INDEPENDENTLY & DIRECTLY FROM THE COMMAND PROMPT
# AND DUE TO THAT IT FUCKING WELL CANNOT FIND THE webapp IN THE PYTHONPATH IF ITS KEPT A SUBDIRECTORY
import sqlite3, datetime, os
import webapp.config as config
from webapp.data_access import _get_open_db_connection, _close_db_connection

def do_work():
    conn = _get_open_db_connection()

    cursor = conn.cursor()
    cursor.executemany("INSERT INTO event_groups (is_enabled, created_on, name_en, created_by_id) VALUES (?,?,?,?);",
                       [
                           (True, datetime.datetime.now(), 'Company Earning Announcements', 1),
                           (True, datetime.datetime.now(), 'OPEC Meetings', 1)
                       ]);
    cursor.close()

    cursor = conn.cursor()
    event_grp_id = cursor.execute("select id from event_groups where name_en = ?", ('Company Earning Announcements',)).fetchone()[0]
    print(event_grp_id)
    company_id = cursor.execute("select id, name_en from companies where argaam_id = ?", (77,)).fetchone()[0]
    print(company_id)
    cursor.close()

    cursor = conn.cursor()
    cursor.executemany("INSERT INTO events(is_enabled, created_on, name_en, type, starts_on, company_id, event_group_id)\
                   VALUES (?,?,?,?,?,?,?);",
                       [
                        (True, datetime.datetime.now(), 'Sabic Q1-2005', 1, datetime.date(2005,4,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2005', 1, datetime.date(2005,7,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2005', 1, datetime.date(2005,10,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2005', 1, datetime.date(2006,1,22), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2006', 1, datetime.date(2006,4,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2006', 1, datetime.date(2006,7,16), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2006', 1, datetime.date(2006,10,15), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2006', 1, datetime.date(2007,1,21), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2007', 1, datetime.date(2007,4,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2007', 1, datetime.date(2007,7,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2007', 1, datetime.date(2007,10,22), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2007', 1, datetime.date(2008,1,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2008', 1, datetime.date(2008,4,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2008', 1, datetime.date(2008,7,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2008', 1, datetime.date(2008,10,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2008', 1, datetime.date(2009,1,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2009', 1, datetime.date(2009,4,20), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2009', 1, datetime.date(2009,7,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2009', 1, datetime.date(2009,10,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2009', 1, datetime.date(2010,1,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2010', 1, datetime.date(2010,4,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2010', 1, datetime.date(2010,7,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2010', 1, datetime.date(2010,10,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2010', 1, datetime.date(2011,1,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2011', 1, datetime.date(2011,4,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2011', 1, datetime.date(2011,7,16), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2011', 1, datetime.date(2011,10,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2011', 1, datetime.date(2012,1,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2012', 1, datetime.date(2012,4,16), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2012', 1, datetime.date(2012,7,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2012', 1, datetime.date(2012,10,16), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2012', 1, datetime.date(2013,1,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2013', 1, datetime.date(2013,4,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2013', 1, datetime.date(2013,7,20), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2013', 1, datetime.date(2013,10,26), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2013', 1, datetime.date(2014,1,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2014', 1, datetime.date(2014,4,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2014', 1, datetime.date(2014,7,19), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2014', 1, datetime.date(2014,10,25), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2014', 1, datetime.date(2015,1,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q1-2015', 1, datetime.date(2015,4,18), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q2-2015', 1, datetime.date(2015,7,25), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q3-2015', 1, datetime.date(2015,10,17), company_id, event_grp_id),
                        (True, datetime.datetime.now(), 'Sabic Q4-2015', 1, datetime.date(2016,1,16), company_id, event_grp_id),
                        ])
    cursor.close()

    cursor = conn.cursor()
    event_grp_id = cursor.execute("select id from event_groups where name_en = ?", ('OPEC Meetings',)).fetchone()[0]
    cursor.close()

    cursor = conn.cursor()
    cursor.executemany("INSERT INTO events(is_enabled, created_on, name_en, type, starts_on, company_id, event_group_id)\
                   VALUES (?,?,?,?,?,?,?);",
                       [
                        (True, datetime.datetime.now(), 'OPEC Meeting - June 2013', 1, datetime.date(2013,6, 14), None, event_grp_id),
                        (True, datetime.datetime.now(), 'OPEC Meeting - Nov 2013', 1, datetime.date(2013, 11, 5), None, event_grp_id),
                        (True, datetime.datetime.now(), 'OPEC Meeting - June 2014', 1, datetime.date(2014, 6, 11), None, event_grp_id),
                        (True, datetime.datetime.now(), 'OPEC Meeting - Nov 2014', 1, datetime.date(2014, 11, 27), None, event_grp_id),
                        (True, datetime.datetime.now(), 'OPEC Meeting - June 2015', 1, datetime.date(2015, 6, 5), None, event_grp_id),
                        (True, datetime.datetime.now(), 'OPEC Meeting - Dec 2015', 1, datetime.date(2015, 12, 4), None, event_grp_id)
                        ])
    cursor.close()

    conn.commit()
    _close_db_connection(conn)

def do_work2():
    conn = _get_open_db_connection()
    cursor = conn.cursor()

    event_grp_id = cursor.execute("select id from event_groups where name_en = ?", ('Company Earning Announcements',)).fetchone()[0]
    print(event_grp_id)

    _close_db_connection(conn)

do_work()
# do_work2()
