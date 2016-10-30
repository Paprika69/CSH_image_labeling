# -*- coding: utf-8 -*-
from flask import request
from flask_restplus import Resource
from app.api.models.image import Image
from app.api.metadata import api
from app import db
from bson.json_util import dumps

ns = api.namespace('hello', description='Operations related to Hello')


@ns.route('/')
class Hello(Resource):
    def get(self):
        image = db.metadata.Image()
        image.img = '1.jpg'
        image.width = 100
        image.height = 120
        image.save()
        return dumps(image), 200