#!/usr/bin/env python3
import requests
import logging


logger = logging.getLogger(__name__)
URL = 'https://api.telegram.org/bot{}'


class Telegram():
    def __init__(self, token):
        logging.debug("__init__")
        self._token = token

    def delete_message(self, chat_id, message_id):
        logging.debug("delete_message")
        url = URL.format(self._token) + '/deleteMessage'
        data = {'chat_id': chat_id, 'message_id': message_id}
        requests.post(url, data=data)

    def send_message(self, chat_id, message, message_thread_id=None,
                     reply_markup=None):
        logging.debug("send_message")
        url = URL.format(self._token) + '/sendMessage'
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        if message_thread_id:
            data['message_thread_id'] = message_thread_id
        if reply_markup:
            data['reply_markup'] = reply_markup
        r = requests.post(url, data=data)
        if r.status_code == 200:
            return r.json()
        return None

    def unban_chat_member(self, chat_id, user_id):
        logging.debug("unban_chat_member")
        url = URL.format(self._token) + '/unbanChatMember'
        data = {'chat_id': chat_id, 'user_id': user_id}
        requests.post(url, data=data)

    def kick_chat_member(self, chat_id, user_id):
        logging.debug("kick_chat_member")
        url = URL.format(self._token) + '/kickChatMember'
        data = {'chat_id': chat_id, 'user_id': user_id}
        requests.post(url, data=data)

    def get_chat_member(self, chat_id, user_id):
        logging.debug("get_chat_member")
        url = URL.format(self._token) + '/getChatMember'
        data = {'chat_id': chat_id, 'user_id': user_id}
        r = requests.post(url, data=data)
        if r.status_code == 200 and 'ok' in r.json() and r.json()['ok']:
            return r.json()['result']
        return None
