#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth

from email.parser import Message, Parser
from email.generator import Generator

# initialization
app = Flask(__name__)

# extensions
auth = HTTPBasicAuth()

# Read config file
app.config.from_object('config')

# Setup logging
if not app.debug:
    import logging

    level = logging.DEBUG
    logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    app.logger.setLevel(level)
    app.logger.addHandler(consoleHandler)

def write_sms(sms):
    result = {'message_id': {}}
    ucs_field = False

    for mobile in sms['mobiles']:
        if not validate_mobile(mobile):
            app.logger.info('Mobile phone %s is not valid [%s]' % (mobile, auth.username()))
            result[mobile] = 'Not valid'
            continue

        if access_mobile(mobile):
            _, msg_file = tempfile.mkstemp(dir=app.config['OUTGOING'],
                                           prefix=app.config['PREFIX'],
                                           suffix='.LOCK')
            text_len = len(sms['text'])

            with open(msg_file, 'w') as fp:
                g = Generator(fp)
                m = Message()

                m.set_header('From', auth.username())
                m.set_header('To', mobile)
                m.set_header('Report', 'yes')

                try:
                    parts_count = text_len / 153 + (text_len % 153 > 0)
                    m.set_payload(sms['text'].encode('us-ascii'))
                    m.set_header('Alphabet', 'ISO')
                except UnicodeEncodeError:
                    parts_count = text_len / 67 + (text_len % 67 > 0)
                    m.set_payload(sms['text'].encode('utf-16-be'))
                    m.set_header('Alphabet', 'UCS2')

                g.close()

            os.rename(msg_file, msg_file[:-5])
            app.logger.info('Message from %s to %s placed to the spooler %s' % (auth.username(), mobile, msg_file))
            message_id = msg_file.split('/')[-1][:-5]
            result['message_id'][mobile] = message_id

        else:
            app.logger.info('Forbidden to send message from %s to %s' % (auth.username(), mobile))
            result['message_id'][mobile] = 'Forbidden'

    result['sent_text'] = sms['text']
    result['parts_count'] = parts_count
    return result

def access_mobile(mobile):
    if not app.config.has_key('MOBILE_PERMS'):
        # Number access control disabled.
        return True

    return mobile in app.config['MOBILE_PERMS'].get(auth.username(), [])

def validate_mobile(mobile):
    return mobile.isdigit()

def bad_request(message):
    response = jsonify({'error': message})
    response.status_code = 400
    return response

@auth.get_password
def get_password(username):
    return app.config['USERS'].get(username)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/v1.0/sms', methods=['GET'])
def get_sent_sms():
    return 'OK'

@app.route('/api/v1.0/sms/sent/<string:message_id>', methods=['GET'])
@auth.login_required
def get_sms(message_id):
    sent_dir = app.config['SENT'] + '/'
    msg_fields = { 'From': None, 'To': None, 'Sent': None, 'message_id': message_id }

    try:
        with open(sent_dir + message_id) as f:
            for line in f:
                for field in msg_fields:
                    s_field = field + ': '
                    if line.startswith(s_field):
                        msg_fields[field] = line.split(s_field)[1].rstrip()
                    if line.startswith('\n'):
                        break
        return jsonify(msg_fields)
    except EnvironmentError:
        return not_found(404)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(exception):
    return make_response(jsonify({'error': 'Internal error'}), 500)

@app.route('/api/v1.0/sms/outgoing', methods=['POST'])
@auth.login_required
def create_sms():
    if not request.json:
        return bad_request('Request error')

    if type(request.json) != dict:
        return bad_request('Request error')

    if not request.json.has_key('mobiles'):
        return bad_request('Request error')

    if not request.json.has_key('text') or type(request.json['text']) != unicode:
        return bad_request('Request error')

    for mobile in request.json['mobiles']:
        if type(mobile) != unicode:
            return bad_request('Request error')

    sms = {
        'mobiles': request.json['mobiles'],
        'text': request.json['text'],
    }

    result = write_sms(sms)
    return jsonify(result), 201
