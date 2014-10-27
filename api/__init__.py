#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask.ext.httpauth import HTTPBasicAuth

# initialization
app = Flask(__name__)

# extensions
auth = HTTPBasicAuth()

# Read config file
app.config.from_object('config')

# Setup logging
if not app.debug and app.config['LOGFILE']:
    import logging
    from logging.handlers import RotatingFileHandler
    level = eval(app.config['LOGFILE'].get('level'))
    file_handler = RotatingFileHandler(app.config['LOGFILE'].get('filename'), maxBytes=app.config['LOGFILE'].get('maxBytes'), backupCount=app.config['LOGFILE'].get('backupCount'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    app.logger.setLevel(level)
    app.logger.addHandler(file_handler)


def write_sms(sms):
    result = {}
    result['message_id'] = {}
    parts_count = 1
    ucs_field = False

    for mobile in sms['mobiles']:
        if not validate_mobile(mobile):
            app.logger.info('Mobile phone %s is not valid [%s]' % (mobile, auth.username()))
            result[mobile] = 'Not valid'
            continue
        if access_mobile(mobile):
            msg_file_lock=tempfile.mkstemp(dir=app.config['OUTGOING'],prefix=app.config['PREFIX'],suffix='.LOCK')[1]
            msg_file = msg_file_lock.split('.LOCK')[0]
            msg_len=len(sms['text'])
            try:
                msg = sms['text'].encode('us-ascii')
                if msg_len > 160:
                    parts_count = msg_len / 152 + (msg_len % 152 > 0)
            except UnicodeEncodeError:
                ucs_field = True
                msg = sms['text'].encode('utf-16-be')
                if msg_len > 70:
                    parts_count = msg_len / 66 + (msg_len % 66 > 0)
            with open(msg_file_lock, 'w') as f:
                f.write('From: ' + auth.username() + '\n')
                if ucs_field:
                    f.write('Alphabet: UCS\n')
                f.write('To: ' + mobile + '\n\n')
                f.write(msg)
                f.close
                os.rename(msg_file_lock, msg_file)
                os.chmod(msg_file, 0666)
                app.logger.info('Message from %s to %s placed to the spooler %s' % (auth.username(), mobile, msg_file))
                message_id = msg_file.split('/')[-1]
            result['message_id'][mobile] = message_id
        else:
            app.logger.info('Forbidden to send message from %s to %s' % (auth.username(), mobile))
            result['message_id'][mobile] = 'Forbidden'
    result['sent_text'] = sms['text']
    result['parts_count'] = parts_count
    return result

def access_mobile(mobile):
    username = auth.username()
    if app.config.has_key('MOBILE_PERMS') and app.config['MOBILE_PERMS'].has_key(username): 
        if mobile in app.config['MOBILE_PERMS'].get(username):
            return True
        else:
            return None
    return True

def validate_mobile(mobile):
    if mobile.isdigit():
        return True
    return False

def bad_request(message):
    response = jsonify({'error': message})
    response.status_code = 400
    return response
    
@auth.get_password
def get_password(username):
    if username in app.config['USERS']:
        return app.config['USERS'].get(username)
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/api/v1.0/sms', methods=['GET'])
def get_sent_sms():
    return 'OK'

@app.route('/api/v1.0/sms/sent/<path:message_id>', methods=['GET'])
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
