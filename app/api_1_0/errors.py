#!/usr/bin/env python

from flask import jsonify, request
from . import api_1_0

@api_1_0.app_errorhandler(400)
def bad_request(exception):
    response = {'status: ': 400, 'message: ': 'Bad request: ' + request.url}
    response['reason'] = (exception)
    response = jsonify(response)
    response.status_code = 400
    return response

def unauthorized(exception):
    response = {'status: ': 401, 'message: ': 'Unauthorized: ' + request.url}
    response['reason'] = (exception)
    response = jsonify(response)
    response.status_code = 401
    return response

@api_1_0.app_errorhandler(403)
def forbidden(exception):
    response = jsonify({'status: ': 403, 'message: ': 'Forbidden: ' + request.url})
    response.status_code = 403
    return response

@api_1_0.app_errorhandler(404)
def not_found(exception):
    response = jsonify({'status: ': 404, 'message: ': 'Not found: ' + request.url})
    response.status_code = 404
    return response

@api_1_0.app_errorhandler(405)
def not_allowed(exception):
    response = jsonify({'status: ': 405, 'message: ': 'Not allowed: ' + request.url})
    response.status_code = 405
    return response

@api_1_0.app_errorhandler(500)
def internal_error(exception):
    response = jsonify({'status: ': 500, 'message: ': 'Internal error: ' + request.url})
    response.status_code = 500
    return response
