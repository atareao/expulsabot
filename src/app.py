#!/usr/bin/env python3
from flask import Flask, jsonify, make_response, abort, url_for, request
from user import User
from apidb import logger, check, init
from telegramapi import Telegram
import threading
import random
import time
import os
import sys
import json
import requests

app = Flask(__name__)


@app.route('/status', methods=['GET'])
def get_status():
    return 'Up and running', 201

def insert_into_influxdb(bot):
    data = '{} value=1'.format('bot' if bot else 'human')
    url = 'https://influxdb.territoriolinux.es/write?db=telegraf'
    headers = {'Content-type': 'application/octet-stream'}
    try:
        res = requests.post(url=url, data=data, headers=headers)
    except Exception:
        logger('Can\'t write in inbluxdb')

def wait_for_new_user(member, chat_id, result):
    time.sleep(int(os.environ['COURTESY_TIME']))
    user = User.get_user(member['id'])
    logger(user)
    logger(json.dumps(result))
    if user.get_timestamp() > 0:
        user.set_timestamp(0)
        user.set_is_bot(True)
        user.save()
        telegram = Telegram(os.environ['TELEGRAM_API_TOKEN'])
        telegram.kick_chat_member(chat_id, member['id'])
        telegram.delete_message(chat_id, result['result']['message_id'])
        insert_into_influxdb(True)

@app.route('/webhook/<webhook>', methods=['GET', 'POST'])
def get_webhook(webhook):
    logger(webhook)
    if os.environ['WEBHOOK'] != webhook:
        return 'KO', 404
    try:
        if request.method == 'GET' or not request.json:
            return 'OK', 200
    except Exception:
        return 'OK', 200
    telegram = Telegram(os.environ['TELEGRAM_API_TOKEN'])
    logger(request.json)
    payload = request.json
    if 'message' in payload and 'new_chat_member' in payload['message']:
        logger('New member')
        member = payload['message']['new_chat_member']
        chat_id = payload['message']['chat']['id']
        user = User.get_user(member['id'])
        if user:
            logger(user)
            delta = int(time.time()) - int(user.get_timestamp())
            if (user.get_timestamp() > 0 and delta > int(os.environ['COURTESY_TIME'])) \
                    or user.get_is_bot():
                user.set_timestamp(0)
                user.set_is_bot(True)
                user.save()
                telegram.kick_chat_member(chat_id, member['id'])
                insert_into_influxdb(True)
        else:
            User.insert_user(member, chat_id)
            rows = []
            buttons = []
            buttons.append({'text': '🐸',
                            'callback_data': 'ko|{}'.format(member['id'])})
            buttons.append({'text': '🤖',
                            'callback_data': 'ko|{}'.format(member['id'])})
            buttons.append({'text': '🐵',
                            'callback_data': 'ko|{}'.format(member['id'])})
            buttons.append({'text': '🐱',
                            'callback_data': 'ko|{}'.format(member['id'])})
            random.shuffle(buttons)
            rows.append(buttons)
            buttons = []
            buttons.append({'text': '🐼',
                            'callback_data': 'ko|{}'.format(member['id'])})
            buttons.append({'text': '🦝', 
                            'callback_data': 'ko|{}'.format(member['id'])})
            buttons.append({'text': '🐧',
                            'callback_data': 'ok|{}'.format(member['id'])})
            buttons.append({'text': '🐮',
                            'callback_data': 'ko|{}'.format(member['id'])})
            random.shuffle(buttons)
            rows.append(buttons)
            random.shuffle(rows)
            inline_keyboard = {'inline_keyboard': rows}
            mention = "<a href=\"tg://user?id={}\">{}</a>".format(
                    member['id'],
                    member['first_name'] if member['first_name'] else 'amig@')
            result = telegram.send_message(
                    chat_id,
                    'Hola {}, selecciona el pingüino, en menos de {} segundos'.format(
                        mention, os.environ['COURTESY_TIME']),
                    json.dumps(inline_keyboard))
            t1 = threading.Thread(target=wait_for_new_user, args=(member,
                chat_id, result))
            t1.start()
    elif 'callback_query' in payload:
        member = payload['callback_query']['from']
        message_id = payload['callback_query']['message']['message_id']
        chat_id = payload['callback_query']['message']['chat']['id']
        result, member_id = payload['callback_query']['data'].split('|')
        logger('Result: {}, Id: {}'.format(result, member_id))
        if int(member_id) == int(member['id']):
            user = User.get_user(member['id'])
            if not user:
                user = User.insert_user(member, chat_id)
            if user and user.get_timestamp() > 0:
                user.set_timestamp(0)
                user.set_is_bot(result == 'ko')
                user.save()
                logger('Chat id: {}, Message id: {}'.format(chat_id, message_id))
                telegram.delete_message(chat_id, message_id)
                if result == 'ko':
                    telegram.kick_chat_member(chat_id, member['id'])
                insert_into_influxdb(result == 'ko')
    elif 'message' in payload:
        from_id = payload['message']['from']['id']
        chat_id = payload['message']['chat']['id']
        message_id = payload['message']['message_id']
        if User.get_bots(from_id):
            telegram.delete_message(chat_id, message_id)
    return 'OK', 201


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    if not check('SELECT * FROM USERS'):
        init()
    app.run(debug=True, host='0.0.0.0')
