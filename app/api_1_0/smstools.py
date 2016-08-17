#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import uuid
from email.parser import Parser
from email.message import Message
from email.generator import Generator
from flask import current_app, request, jsonify
from .authentication import auth
from .errors import not_found, forbidden

def access_mobile(mobile):
    if not 'USER_WHITELIST' in current_app.config.keys():
        # Number access control disabled.
        return True
    if current_app.config['USER_WHITELIST'].get(auth.username()):
        return mobile in current_app.config['USER_WHITELIST'].get(auth.username(), [])
    else:
        return True

def validate_mobile(mobile):
    return re.match(r'^\+?\d+$', mobile) and True

def list_some_sms(kind):
    if kind not in current_app.config['KINDS']:
        return not_found(None)

    limit = current_app.config.get('LIMIT') or False
    message_ids = os.listdir(current_app.config[kind.upper()])
    message_ids = [mid for mid in message_ids if not mid.endswith('.LOCK')]
    total_count = len(message_ids)
    result = {}
    result['total_count'] = total_count
    result['limit'] = limit
    result['message_id'] = message_ids[:limit] if limit else message_ids

    return jsonify(result)

def get_some_sms(kind, message_id):
    if kind not in current_app.config['KINDS']:
        return not_found(None)
    try:
        with open(os.path.join(current_app.config[kind.upper()], message_id)) as fp:
            p = Parser()
            m = p.parse(fp)

            if m.get('Alphabet', '').startswith('UCS'):
                charset = 'utf-16-be'
            else:
                # Since UTF-8 is backwards compatible with US-ASCII and
                # outgoing messages sent from the command line will be
                # in UTF-8 without an Alphabet option, this will work.
                charset = 'utf-8'

            m.add_header('message_id', message_id)
            m.add_header('text', m.get_payload())
            result = dict(m)
            if result['From'] == auth.username():
                return jsonify(result)
            elif 'ADMIN_ACCOUNTS' in current_app.config and auth.username() in current_app.config['ADMIN_ACCOUNTS']:
                return jsonify(result)
            else:
                return forbidden(None)
    except EnvironmentError:
        return not_found(None)

def detect_coding(text):
    text_len=len(text)
    try:
        parts_count = text_len / 153 + (text_len % 153 > 0)
        text = text.encode('iso8859-15')
        coding = 'ISO'
    except UnicodeEncodeError:
        parts_count = text_len / 67 + (text_len % 67 > 0)
        text = text.encode('utf-16-be')
        coding = 'UCS2'

    return text, coding, parts_count

def send_sms(data):
    text, coding, parts_count = detect_coding(data['text'])

    result = {
        'sent_text': data['text'],
        'parts_count': parts_count,
        'mobiles': {}
    }

    for mobile in data['mobiles']:
        # generate message_id
        message_id = str(uuid.uuid4())

        result['mobiles'][mobile] = {}
        result['mobiles'][mobile]['message_id'] = message_id
        result['mobiles'][mobile]['dlr_status'] = os.path.join(os.path.dirname(request.url),
                                                  os.path.basename(current_app.config['SENT']), message_id)

        if not validate_mobile(mobile):
            current_app.logger.info('Message from [%s] to [%s] have invalid mobile number' % (auth.username(), mobile))
            result['mobiles'][mobile]['response'] = 'Failed: invalid mobile number'
            continue

        if access_mobile(mobile):
            lock_file = os.path.join(current_app.config['OUTGOING'], message_id + '.LOCK')
            m = Message()
            m.add_header('From', auth.username())
            m.add_header('To', mobile)
            m.add_header('Alphabet', coding)
            m.set_payload(text)

            with open(lock_file, 'w') as fp:
                fp.write(m.as_string())

            msg_file = lock_file.split('.LOCK')[0]
            os.rename(lock_file, msg_file)
            os.chmod(msg_file, 0o660)
            current_app.logger.info('Message from [%s] to [%s] placed to the spooler as [%s]' % (auth.username(), mobile, msg_file))
            result['mobiles'][mobile]['response'] = 'Ok'
        else:
            current_app.logger.info('Message from [%s] to [%s] have forbidden mobile number' % (auth.username(), mobile))
            current_app.logger.info('Forbidden to send message from [%s] to [%s]' % (auth.username(), mobile))
            result['mobiles'][mobile]['response'] = 'Failed: forbidden mobile number'

    return result
