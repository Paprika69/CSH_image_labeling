# -*- coding: utf-8 -*-
# metadata/app/api/metadata.py

from flask_restplus import Api

api = Api(version='1.0', title='Hello API', description='this is my first API')


@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occured"
    return {message: message}, 500