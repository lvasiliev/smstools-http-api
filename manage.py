#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api import app
from flask.ext.script import Manager

# extensions
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
