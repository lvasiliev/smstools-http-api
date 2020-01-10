#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config:

    # Valid message kinds (also spooler directories).
    KINDS = ['incoming', 'outgoing', 'checked', 'failed', 'sent']

    # Accounts who may access to all messages
    #ADMIN_ACCOUNTS = ['superadm']

    # Default queue for send message, if not set, keep smsd choose the default queue
    #DEFAULTQUEUE = "GSM1"

    # Limit for list messages of given kind.
    #LIMIT = 10000

    # Whitelist for users
    #USER_WHITELIST = {
    #    'lvv': [ '911' ],
    #}

    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):

    # Smsd spool path
    INCOMING = "/var/spool/sms/incoming"
    OUTGOING = "/var/spool/sms/outgoing"
    CHECKED  = "/var/spool/sms/checked"
    FAILED   = "/var/spool/sms/failed"
    SENT     = "/var/spool/sms/sent"

    # Users database (htpasswd format)
    # Generate hash: openssl passwd -apr1 PASSWORD
    # username:$apr1$qSS22H6v$sem/.bUQXjGUIIHb.MXLw1
    HTPASSWD_PATH="/usr/local/etc/smstools-http-api/htpasswd.users"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging

        level = logging.INFO
        logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        app.logger.setLevel(level)
        app.logger.addHandler(consoleHandler)

class DevelopmentConfig(Config):
    DEBUG = True

    # Smsd spool path
    INCOMING = "tmp/incoming"
    OUTGOING = "tmp/outgoing"
    CHECKED  = "tmp/checked"
    FAILED   = "tmp/failed"
    SENT     = "tmp/sent"

    # Users database (htpasswd format)
    # Generate hash: openssl passwd -apr1 PASSWORD
    # username:$apr1$qSS22H6v$sem/.bUQXjGUIIHb.MXLw1
    HTPASSWD_PATH="htpasswd.users"

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    OUTGOING = "outgoing"
    SENT = "sent"
    HTPASSWD_PATH = "htpasswd.users"

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
