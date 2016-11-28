# -*- coding: utf-8 -*-
# metadata/app/api/metadata.py

from flask_restplus import Api

api = Api(version='1.0', title='Metadata API', description='APIs for labeling images')


@api.errorhandler
def default_error_handler(e):
    message = "An unhandled exception occured"
    return {message: message}, 500