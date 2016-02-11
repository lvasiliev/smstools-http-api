# -*- coding: utf-8 -*-

import base64
import codecs
import crypt
from hashlib import md5, sha1

# From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/325204
def apache_md5crypt(password, salt, magic='$apr1$'):
    """
    Calculates the Apache-style MD5 hash of a password
    """
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    magic = magic.encode('utf-8')

    m = md5()
    m.update(password + magic + salt)

    mixin = md5(password + salt + password).digest()
    for i in range(0, len(password)):
        m.update(mixin[i % 16])

    i = len(password)
    while i:
        if i & 1:
            m.update('\x00')
        else:
            m.update(password[0])
        i >>= 1

    final = m.digest()

    for i in range(1000):
        m2 = md5()
        if i & 1:
            m2.update(password)
        else:
            m2.update(final)

        if i % 3:
            m2.update(salt)

        if i % 7:
            m2.update(password)

        if i & 1:
            m2.update(final)
        else:
            m2.update(password)

        final = m2.digest()

    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    rearranged = ''
    seq = ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5))
    for a, b, c in seq:
        v = ord(final[a]) << 16 | ord(final[b]) << 8 | ord(final[c])
        for i in range(4):
            rearranged += itoa64[v & 0x3f]
            v >>= 6

    v = ord(final[11])
    for i in range(2):
        rearranged += itoa64[v & 0x3f]
        v >>= 6

    return magic + salt + '$' + rearranged

def check_password(test_password, password):
    if password.startswith('$apr1$'):
        salt = password.strip('$').split('$')[1]
        check = apache_md5crypt(test_password, salt)
    elif password.startswith('{SHA}'):
        _hash = sha1(test_password.encode('utf-8')).digest()
        check = '{SHA}' + base64.b64encode(_hash)
    else:
        check = crypt.crypt(test_password.encode('utf-8'), password)

    return check == password

def read_htpasswd(path):
    f = codecs.open(path, 'r', 'utf-8')
    try:
        users = {}
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                username, password = line.split(':', 1)
            except ValueError:
                continue

            users[username] = password

        return users
    finally:
        f.close()
