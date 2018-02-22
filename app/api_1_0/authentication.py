#!/usr/bin/env python

from flask import current_app, g
from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized
from passlib.apache import HtpasswdFile

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(login, password):
    try:
        htpasswd_file = HtpasswdFile(current_app.config['HTPASSWD_PATH'])
    except EnvironmentError:
        return False

    if htpasswd_file.check_password(login, password):
        return True
    else:
        g.reason = 'invalid password'

    return False

@auth.error_handler
def auth_error():
    try:
        return unauthorized('Unauthorized access: %s' % g.reason)
    except AttributeError:
        return unauthorized('Unauthorized access')
