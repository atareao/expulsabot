#!/usr/bin/env python3
import requests
from apidb import logger
import json

URL = 'https://api.telegram.org/bot{}'

class Telegram():
    def __init__(self, token):
        self._token = token

    def delete_message(self, chat_id, message_id):
        url = URL.format(self._token) + '/deleteMessage'
        data = {'chat_id': chat_id, 'message_id': message_id}
        requests.post(url, data=data)

    def send_message(self, chat_id, message, reply_markup=None):
        url = URL.format(self._token) + '/sendMessage'
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        if reply_markup:
            data['reply_markup'] = reply_markup
        r = requests.post(url, data=data)
        if r.status_code == 200:
            return r.json()
        return None

    def unban_chat_member(self, chat_id, user_id):
        url = URL.format(self._token) + '/unbanChatMember'
        data = {'chat_id': chat_id, 'user_id': user_id}
        requests.post(url, data=data)

    def kick_chat_member(self, chat_id, user_id):
        url = URL.format(self._token) + '/kickChatMember'
        data = {'chat_id': chat_id, 'user_id': user_id}
        requests.post(url, data=data)
