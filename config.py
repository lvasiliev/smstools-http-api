# Smsd spool path
OUTGOING="/var/spool/sms/outgoing"
SENT="/var/spool/sms/sent"
PREFIX="smsgw.http."

# Logfile options
LOGFILE= {
    "filename": "/var/log/smsd/smstools-http-api.log",
    "maxBytes": 512000,
    "backupCount": 10,
    "level": "logging.DEBUG",
}

# Basic auth database
USERS = {
    "lvv": "SecretPAss",
}

# Access to mobile phone if need
#MOBILE_PERMS = {
#    'lvv': [ '911' ],
#}
