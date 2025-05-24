#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Expulsabot module"""
import threading
import random
import time
import os
import json
import sys
from user import User
from apidb import check, init
from telegramapi import Telegram
from dotenv import load_dotenv
import logging
from openobserve import OpenObserve


logging.basicConfig(
    stream=sys.stdout,
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def wait_for_new_user(member, chat_id, result, openobserve):
    logger.debug("wait_for_new_user")
    """
    Wait for the answer of the new user

    :param member dict: Them member
    :param chat_id str: The chat id
    :param result str: The result
    """
    time.sleep(float(os.getenv('COURTESY_TIME', '120')))
    user = User.get_user(member['id'])
    logger.debug(user)
    logger.debug(json.dumps(result))
    if user is not None and user.get_timestamp() > 0:
        user.set_timestamp(0)
        user.set_is_bot(True)
        user.save()
        telegram = Telegram(os.environ['TELEGRAM_API_TOKEN'])
        telegram.kick_chat_member(chat_id, member['id'])
        telegram.delete_message(chat_id, result['result']['message_id'])
        status = "banned"
    else:
        status = "waiting"
    payload = {
        "chat_id": chat_id,
        "status": status,
        "member": member
    }
    openobserve.post("expulsabot", payload)


def do_kick_user(telegram, user, member, chat_id, openobserve):
    logger.debug("do_kick_user")
    """
    Kick an user

    :param telegram Telegram: Telegram obkect
    :param user User: an user
    :param member dict: Member
    :param chat_id str: chat id
    """
    logger.debug(user)
    delta = int(time.time()) - int(user.get_timestamp())
    if (user.get_timestamp() > 0 and
        delta > int(os.getenv('COURTESY_TIME', '120'))) \
            or user.get_is_bot():
        user.set_timestamp(0)
        user.set_is_bot(True)
        user.save()
        telegram.kick_chat_member(chat_id, member['id'])
        payload = {
            "chat_id": chat_id,
            "status": "banned",
            "member": member
        }
        openobserve.post("expulsabot", payload)


def do_query_user(telegram, member, chat_id, openobserve,
                  message_thread_id=None):
    logger.debug("do_query_user")
    """
    Show a keyboard

    :param telegram Telegram: Telegram object
    :param member dict: Member
    :param chat_id str: chat id
    """
    User.insert_user(member)
    rows = []
    buttons = []
    buttons.append({'text': '🐸',
                    'callback_data': f"ko|{member['id']}"})
    buttons.append({'text': '🤖',
                    'callback_data': f"ko|{member['id']}"})
    buttons.append({'text': '🐵',
                    'callback_data': f"ko|{member['id']}"})
    buttons.append({'text': '🐱',
                    'callback_data': f"ko|{member['id']}"})
    random.shuffle(buttons)
    rows.append(buttons)
    buttons = []
    buttons.append({'text': '🐼',
                    'callback_data': f"ko|{member['id']}"})
    buttons.append({'text': '🦝',
                    'callback_data': f"ko|{member['id']}"})
    buttons.append({'text': '🐧',
                    'callback_data': f"ok|{member['id']}"})
    buttons.append({'text': '🐮',
                    'callback_data': f"ko|{member['id']}"})
    random.shuffle(buttons)
    rows.append(buttons)
    random.shuffle(rows)
    inline_keyboard = {'inline_keyboard': rows}
    name = member['first_name'] if member['first_name'] else 'amig@'
    mention = f"<a href=\"tg://user?id={member['id']}\">{name}</a>"
    courtesy_time = os.getenv('COURTESY_TIME', '120')
    msg = (f"Hola {mention}, selecciona el pingüino, "
           f"en menos de {courtesy_time} segundos")
    result = telegram.send_message(
        chat_id,
        msg,
        message_thread_id,
        json.dumps(inline_keyboard))
    thread_1 = threading.Thread(target=wait_for_new_user,
                                args=(member, chat_id, result, openobserve))
    thread_1.start()


def do_telegram_callback_query(telegram, payload, openobserve):
    logger.debug("do_telegram_callback_query")
    """
    The callback query

    :param telegram Telegram: The telegram object
    :param payload dict: The payload
    """
    member = payload['callback_query']['from']
    message_id = payload['callback_query']['message']['message_id']
    chat_id = payload['callback_query']['message']['chat']['id']
    result, member_id = payload['callback_query']['data'].split('|')
    logger.debug(f"Result: {result}, Id: {member_id}")
    if int(member_id) == int(member['id']):
        user = User.get_user(member['id'])
        if not user:
            user = User.insert_user(member)
        if user is not None and user.get_timestamp() > 0:
            user.set_timestamp(0)
            user.set_is_bot(result == 'ko')
            user.save()
            logger.debug(f"Chat id: {chat_id}, Message id: {message_id}")
            telegram.delete_message(chat_id, message_id)
            if result == 'ko':
                telegram.kick_chat_member(chat_id, member['id'])
                status = 'banned'
            else:
                status = 'accepted'
            payload = {
                "chat_id": chat_id,
                "status": status,
                "member": member
            }
            openobserve.post("expulsabot", payload)


def do_telegram_mesage(telegram, payload):
    logger.debug("do_telegram_mesage")
    """
    Process a telegram message

    :param telegram Telegram: Telegram
    :param payload dict: Data
    """
    from_id = payload['message']['from']['id']
    chat_id = payload['message']['chat']['id']
    message_id = payload['message']['message_id']
    if "message_thread_id" in payload['message']:
        message_thread_id = payload['message']['message_thread_id']
    else:
        message_thread_id = None
    if User.get_bots(from_id):
        telegram.delete_message(chat_id, message_id)
    elif 'entities' in payload['message']:
        for entity in payload['message']['entities']:
            if 'type' in entity and entity['type'] == 'bot_command':
                instruction = payload['message']['text']
                start = entity['offset'] + 1
                end = start + entity['length']
                command = instruction[start:end - 1]
                args = instruction[end:]
                do_telegram_command(chat_id, message_id, message_thread_id,
                                    from_id, command, args)
                break


def do_telegram_command(chat_id, message_id, message_thread_id, from_id,
                        command, args):
    logger.debug("do_telegram_command")
    """
    Process a telegram command

    :param chat_id str: chat id
    :param message_id str: message id
    :param from_id str: sender id
    :param command str: command
    :param args list: arguments
    """
    telegram = Telegram(os.environ['TELEGRAM_API_TOKEN'])
    if command == 'unban':
        telegram.delete_message(chat_id, message_id)
        user = telegram.get_chat_member(chat_id, from_id)
        if user is not None and 'status' in user and \
                user['status'] in ['creator', 'administrator']:
            user = User.get_user(args)
            message = 'Mission failed'
            if user:
                user.set_timestamp(0)
                user.set_is_bot(False)
                user.save()
                user = User.get_user(args)
                if user and user.get_is_bot() is False:
                    message = 'Mission accomplished'
            telegram.send_message(chat_id, message, message_thread_id)


def main():
    telegram_token = os.environ.get('TELEGRAM_API_TOKEN')
    timeout = int(os.getenv('TELEGRAM_TIMEOUT', '300'))
    openobserve_url = os.getenv('OPENOBSERVE_URL')
    openobserve_token = os.getenv('OPENOBSERVE_API_TOKEN')
    telegram = Telegram(telegram_token, timeout)
    openobserve = OpenObserve(openobserve_url, openobserve_token)
    last_update_id = None
    while True:
        logger.debug("Waiting")
        try:
            updates = telegram.get_updates(offset=last_update_id)
            logger.debug(f"Updates: {updates}")
            if updates:
                last_update_id = updates[-1]['update_id'] + 1
            for update in updates:
                logger.debug(update)
                if 'message' in update and 'new_chat_member' in update['message']:
                    member = update['message']['new_chat_member']
                    chat_id = update['message']['chat']['id']
                    user = User.get_user(member['id'])
                    if user:
                        do_kick_user(telegram, user, member, chat_id,
                                     openobserve)
                    else:
                        do_query_user(telegram, member, chat_id, openobserve)
                elif 'callback_query' in update:
                    do_telegram_callback_query(telegram, update, openobserve)
                elif 'message' in update:
                    do_telegram_mesage(telegram, update)
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == '__main__':
    load_dotenv()
    if not check('SELECT * FROM USERS'):
        init()
    main()
