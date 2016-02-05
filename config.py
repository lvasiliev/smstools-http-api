# Smsd spool path
OUTGOING="/var/spool/sms/outgoing"
SENT="/var/spool/sms/sent"
PREFIX="smsgw.http."

# hash passwords with PBKDF2/SHA1, using werkzeug's password hashing utility functions
HASHED_PASSWORDS = False

# if you hash passwords with a different number of iterations, put it in this setting
# to avoid a timing side channel
DEFAULT_HASH_ITERATIONS = 10000

# Basic auth database
# note: if using hashed passwords, they must be in a format understood
# by werkzeug.security.check_password_hash
# (see http://werkzeug.pocoo.org/docs/0.11/utils/#werkzeug.security.check_password_hash )
# the helper script create_hashed_password is provided to generate password hashes
USERS = {
    "lvv": "SecretPAss",
    # example of a hashed password:
    # 'foo': 'pbkdf2:sha1:10000$JJzAUxHz$435b72f9585e9bf490b1776f63a5716a21ce040d'
}

# Access to mobile phone if need
#MOBILE_PERMS = {
#    'lvv': [ '911' ],
#}
