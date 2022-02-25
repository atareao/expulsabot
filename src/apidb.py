#!/usr/bin/env python3
import sqlite3
import time
import os
import sys


DATABASE = '/app/database/expulsabot.db'
TABLE_USERS = """
CREATE TABLE IF NOT EXISTS USERS(
ID INTEGER PRIMARY KEY AUTOINCREMENT,
TELEGRAM_ID TEXT,
TIMESTAMP INTEGER,
IS_BOT INTEGER);
"""


def logger(message, force=False):
    if force or (os.environ['DEBUG'] and os.environ['DEBUG'].lower() == 'true'):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        sys.stdout.write('{} | {}\n'.format(timestamp, message))


def init():
    logger('Create tables in database')
    execute(TABLE_USERS)


def execute(sqlquery, data=None):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        logger(sqlquery)
        if data:
            cursor.execute(sqlquery, data)
        else:
            cursor.execute(sqlquery)
        conn.commit()
    except Exception as e:
        logger(e, True)
    finally:
        if conn:
            conn.close()


def select(sqlquery, one=False):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(sqlquery)
        if one:
            return cursor.fetchone()
        return cursor.fetchall()
    except Exception as e:
        logger(e, True)
    finally:
        if conn:
            conn.close()


def check(sqlquery):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(sqlquery)
        return True
    except Exception as e:
        logger(e, True)
    finally:
        if conn:
            conn.close()
    return False
