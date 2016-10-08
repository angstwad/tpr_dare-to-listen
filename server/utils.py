# -*- coding: utf-8 -*-
from flask import make_response


def two_oh_one():
    resp = make_response()
    resp.status_code = 201
    return resp


def boolify(value):
    if value is None:
        return True
    if value.lower() == 'true':
        return True
    return False
