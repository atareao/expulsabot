#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""user"""
import time
import hashlib
import logging
from apidb import execute, select

logger = logging.getLogger(__name__)
BOT = 0
HUMAN = 1


def hashea(code):
    h = hashlib.md5()
    h.update(str(code).encode('utf-8'))
    return h.hexdigest()


class User():
    def __init__(self):
        logger.debug("__init__")
        self._id = None
        self._telegram_id = None
        self._timestamp = 0
        self._is_bot = None

    def get_id(self):
        logger.debug("get_id")
        return self._id

    def get_telegram_id(self):
        logger.debug("get_telegram_id")
        return self._telegram_id

    def get_timestamp(self):
        logger.debug("get_timestamp")
        return self._timestamp

    def set_timestamp(self, timestamp):
        logger.debug("set_timestamp")
        self._timestamp = timestamp

    def get_is_bot(self):
        logger.debug("get_is_bot")
        return self._is_bot == BOT

    def set_is_bot(self, is_bot):
        logger.debug("set_is_bot")
        self._is_bot = BOT if is_bot else HUMAN

    @classmethod
    def parse(cls, data):
        logger.debug("parse")
        user = User()
        user._id = data[0]
        user._telegram_id = data[1]
        user._timestamp = data[2]
        user._is_bot = data[3]
        return user

    def save(self):
        logger.debug("save")
        sqlquery = 'UPDATE USERS SET TIMESTAMP=?, IS_BOT=? WHERE TELEGRAM_ID=?'
        logger.debug(sqlquery)
        data = (self._timestamp, self._is_bot, self._telegram_id)
        execute(sqlquery, data)

    @classmethod
    def get_bots(cls, telegram_id=None):
        logger.debug("get_bots")
        bots = []
        sqlquery = 'SELECT * FROM USERS WHERE (TIMESTAMP > 0 OR IS_BOT = 0)'
        if telegram_id:
            sqlquery += ' AND TELEGRAM_ID = \'{}\''.format(hashea(telegram_id))
        logger.debug(sqlquery)
        result = select(sqlquery)
        if result:
            for item in result:
                bots.append(cls.parse(item))
        return bots

    @classmethod
    def get_user(cls, telegram_id):
        logger.debug("get_user")
        sqlquery = 'SELECT * FROM USERS WHERE TELEGRAM_ID=\'{}\''.format(
            hashea(telegram_id))
        logger.debug(sqlquery)
        result = select(sqlquery, True)
        if result:
            return cls.parse(result)
        return None

    @classmethod
    def unban(cls, user_id):
        logger.debug("unban")
        sqlquery = ('UPDATE USERS SET IS_BOT = ?, TIMESTAMP = 0 '
                    'WHERE TELEGRAM_ID = ?')
        logger.debug(sqlquery)
        data = (HUMAN, hashea(user_id))
        logger.debug(data)
        execute(sqlquery, data)
        return cls.get_user(user_id)

    @classmethod
    def insert_user(cls, member, is_bot=False):
        logger.debug("insert_user")
        sqlquery = ('INSERT INTO USERS '
                    '(TELEGRAM_ID, TIMESTAMP, IS_BOT) '
                    'VALUES(?, ?, ?)')
        logger.debug(sqlquery)
        if is_bot or member['is_bot']:
            is_bot = BOT
        else:
            is_bot = HUMAN
        data = (hashea(member['id']), int(time.time()), is_bot)
        execute(sqlquery, data)
        return cls.get_user(member['id'])

    def __str__(self):
        logger.debug("__str__")
        user = 'Id: {}\n'.format(self._id)
        user += 'Telegram Id: {}\n'.format(self._telegram_id)
        user += 'Timestamp: {}\n'.format(self._timestamp)
        user += 'Is bot: {}\n'.format(self._is_bot == BOT)
        return user
