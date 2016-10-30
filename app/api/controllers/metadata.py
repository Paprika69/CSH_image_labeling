# -*- coding: utf-8 -*-
from flask import request
from flask_restplus import Resource
from app.api.models.image import Image
from app.api.metadata import api
from app import db
from bson.json_util import dumps
import os
import imagesize
import math

ns = api.namespace('metadata', description='Operations related to metadata')


@ns.route('/db')
class MetadataWriter(Resource):
    def get(self):
        img_path = os.getcwd() + "/app/static/metadata"
        files = os.listdir(img_path)
        result = {"success": True, "message": str(len(files)) + " records imported successfully"}
        for f in files:
            image = db.metadata.Image()
            image.img = f
            image.size = os.path.getsize(img_path + "/" + f)
            image.width, image.height = imagesize.get(img_path + "/" + f)
            image.ratio = round(image.width*1.0/image.height, 3)
            image.save()
        db.close()
        return result, 200


@ns.route('/<int:page>')
class MetadataReader(Resource):
    def get(self, page):
        page_size = 4
        records = db.metadata.Image.find().sort([('ratio', -1)]).skip((page-1)*page_size).limit(page_size)
        total = db.metadata.Image.find().count()
        db.close()
        result = {
            "total_page": int(math.ceil(total*1.0 / page_size)),
            "total": total,
            "current": page,
            "data": records
        }
        return dumps(result), 200


@ns.route('/label')
class MetadataLabel(Resource):
    def post(self):
        frm = request.form
        record = db.metadata.Image.find_and_modify({'img': frm.get('img')}, {
            "$set": {
                'label': frm.get('label')
            }
        })

        return dumps(record), 200


@ns.route('/status')
class MetadataStatus(Resource):
    def post(self):
        frm = request.form
        record = db.metadata.Image.find_and_modify({'img': frm.get('img')}, {
            "$set": {
                'status': frm.get('status')
            }
        })

        return dumps(record), 200


@ns.route('/query')
class MetadataQuery(Resource):
    def post(self):
        page_size = 2
        frm = request.json

        page = frm['page']
        condition = frm['condition']
        total = db.metadata.Image.fetch(condition).count()
        records = db.metadata.Image.fetch(condition).sort([('ratio', -1)]).skip((page -1) * page_size).limit(page_size)
        db.close()
        result = {
            "total_page": int(math.ceil(total * 1.0 / page_size)),
            'total': total,
            "current": page,
            "data": records
        }

        return dumps(records), 200