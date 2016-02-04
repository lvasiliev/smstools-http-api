#! /usr/bin/env python2
from __future__ import print_function

import sys
from werkzeug.security import generate_password_hash

DEFAULT_ITERATIONS = 10000
METHOD_PREFIX = 'pbkdf2:sha1:'

usage = (
'''usage: {name} password [iterations]
Generate a hash of <password> using <iterations> iterations. If <iterations> defaults to {num_iterations} if not specified.
'''.format(name=sys.argv[0], num_iterations=DEFAULT_ITERATIONS)
)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(usage)
        return

    password = sys.argv[1]
    iterations = DEFAULT_ITERATIONS
    if len(sys.argv) > 2:
        iterations = int(sys.argv[2]) # verify that the arg is an int

    method = METHOD_PREFIX + str(iterations)

    print(generate_password_hash(password, method))


if __name__ == '__main__':
    main()

