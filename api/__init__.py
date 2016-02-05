#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from tempfile import mkstemp
from os.path import basename, join as mkpath
from os import rename, listdir, chmod

from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth

from email.parser import Message, Parser
from email.generator import Generator

# initialization
app = Flask(__name__)

# extensions
auth = HTTPBasicAuth()

# Read config file
app.config.from_object('config')

# Valid message kinds (also spooler directories).
KINDS = ['incoming', 'outgoing', 'checked', 'failed', 'sent']

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
    result = {
        'message_id': {},
        'sent_text': sms['text'],
        'parts_count': 0,
    }
    parts_count = 0

    for mobile in sms['mobiles']:
        if not validate_mobile(mobile):
            app.logger.info('Mobile phone %s is not valid [%s]' % (mobile, auth.username()))
            result[mobile] = 'Not valid'
            continue

        if access_mobile(mobile):
            _, lock_file = mkstemp(dir=app.config['OUTGOING'],
                                   prefix=app.config['PREFIX'],
                                   suffix='.LOCK')
            text_len = len(sms['text'])

            m = Message()
            m.add_header('From', auth.username())
            m.add_header('To', mobile)

            try:
                result['parts_count'] = text_len / 153 + (text_len % 153 > 0)
                m.set_payload(sms['text'].encode('us-ascii'))
                m.add_header('Alphabet', 'ISO')
            except UnicodeEncodeError:
                result['parts_count'] = text_len / 67 + (text_len % 67 > 0)
                m.set_payload(sms['text'].encode('utf-16-be'))
                m.add_header('Alphabet', 'UCS2')

            with open(lock_file, 'w') as fp:
                fp.write(m.as_string())

            msg_file = lock_file[:-5]
            rename(lock_file, msg_file)
            chmod(msg_file, 0660)
            app.logger.info('Message from %s to %s placed to the spooler as %s' % (auth.username(), mobile, msg_file))
            result['message_id'][mobile] = basename(msg_file)

        else:
            app.logger.info('Forbidden to send message from %s to %s' % (auth.username(), mobile))
            result['message_id'][mobile] = 'Forbidden'

    return result

def access_mobile(mobile):
    if not app.config.has_key('MOBILE_PERMS'):
        # Number access control disabled.
        return True

    return mobile in app.config['MOBILE_PERMS'].get(auth.username(), [])

def validate_mobile(mobile):
    return re.match(r'^\+?\d+$', mobile) and True

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

@app.route('/api/v1.0/sms')
@auth.login_required
def get_sms():
    return jsonify({})

@app.route('/api/v1.0/sms/<kind>/')
@auth.login_required
def list_some_sms(kind):
    if kind not in KINDS:
        return not_found(None)

    return jsonify({'message_id': listdir(app.config[kind.upper()])})

@app.route('/api/v1.0/sms/<kind>/<message_id>')
@auth.login_required
def get_some_sms(kind, message_id):
    if kind not in KINDS:
        return not_found(None)

    try:
        with open(mkpath(app.config[kind.upper()], message_id)) as fp:
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
            m.add_header('text', m.get_payload().decode(charset))
            return jsonify(dict(m))

    except EnvironmentError:
        return not_found(None)

@app.errorhandler(404)
def not_found(exception):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(exception):
    return make_response(jsonify({'error': 'Internal error'}), 500)

@app.route('/api/v1.0/sms/outgoing', methods=['POST'])
@auth.login_required
def create_sms():
    if not request.json:
        return bad_request('Body is not a valid JSON object')

    if not isinstance(request.json, dict):
        return bad_request('Body is not a valid JSON object')

    if not request.json.has_key('mobiles'):
        return bad_request('Body is missing the "mobiles" key')

    if not request.json.has_key('text'):
        return bad_request('Body is missing the "text" key')

    if not isinstance(request.json['text'], unicode):
        return bad_request('Body field "text" is not a string')

    if not isinstance(request.json['mobiles'], list):
        return bad_request('Body field "mobiles" is not a list of strings')

    for mobile in request.json['mobiles']:
        if type(mobile) != unicode:
            return bad_request('Body field "mobiles" is not a list of strings')

    sms = {
        'mobiles': request.json['mobiles'],
        'text': request.json['text'],
    }

    result = write_sms(sms)
    return jsonify(result), 201

# vim:set sw=4 ts=4 et:
