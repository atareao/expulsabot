#!/usr/bin/env python3
import os
import sqlite3
import logging


DATABASE = os.getenv("DATABASE", "expulsabot.db")
TABLE_USERS = """
CREATE TABLE IF NOT EXISTS USERS(
ID INTEGER PRIMARY KEY AUTOINCREMENT,
TELEGRAM_ID TEXT,
TIMESTAMP INTEGER,
IS_BOT INTEGER);
"""

logger = logging.getLogger(__name__)


def init():
    logger.debug('Create tables in database')
    execute(TABLE_USERS)


def execute(sqlquery, data=None):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        logger.debug(sqlquery)
        if data:
            cursor.execute(sqlquery, data)
        else:
            cursor.execute(sqlquery)
        conn.commit()
    except Exception as e:
        logger.error(e, True)
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
        logger.error(e, True)
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
        logger.error(e, True)
    finally:
        if conn:
            conn.close()
    return False
