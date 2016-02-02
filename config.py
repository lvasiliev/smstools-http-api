# Smsd spool path
INCOMING = "/var/spool/sms/incoming"
OUTGOING = "/var/spool/sms/outgoing"
CHECKED  = "/var/spool/sms/checked"
FAILED   = "/var/spool/sms/failed"
SENT     = "/var/spool/sms/sent"

PREFIX = "smsgw.http."

# Basic auth database
USERS = {
    "lvv": "SecretPAss",
}

# Access to phone number if needed
#MOBILE_PERMS = {
#    'lvv': [ '911' ],
#}
