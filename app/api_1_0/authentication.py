#!/usr/bin/env python

from flask import current_app, g
from flask.ext.httpauth import HTTPBasicAuth
from .errors import unauthorized

from ..lib.htpasswd import check_password, read_htpasswd
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(login, password):
    try:
        users_ht = read_htpasswd(current_app.config['HTPASSWD_PATH'])
    except EnvironmentError:
        return False

    if login in users_ht:
        password_hash = users_ht[login]
        if check_password(password, password_hash):
            return True
        else:
            g.reason = 'invalid password'
    else:
        g.reason = 'invalid login'

    return False

@auth.error_handler
def auth_error():
    try:
        return unauthorized('Unauthorized access: %s' % g.reason)
    except AttributeError:
        return unauthorized('Unauthorized access')
