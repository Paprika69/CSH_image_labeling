# -*- coding: utf-8 -*-
from flask import request
from flask_restplus import Resource
from app.api.models.image import Image
from app.api.metadata import api
from app import db, tran, REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD
from bson.json_util import dumps, loads
import os
import ssh

ns = api.namespace('metadata', description='Operations related to metadata')


@ns.route('/db')
class MetadataWriter(Resource):
    def get(self):
        img_path = "app/static/metadata"

        remote_img_path = "/export/CSH/projects/word_extraction/anonymized_words/"
        client = ssh.SSHClient()
        client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        client.connect(REMOTE_HOST, port=22, username=REMOTE_USER, password=REMOTE_PASSWORD)
        sftp = client.open_sftp()

        records = tran.Image.find().limit(1000)
        result = {"success": True,
                  "message": "the size of " + str(records.count()) + " records updated successfully"}
        for record in records:
            sftp.get(remote_img_path + record["anonymizedImageFile"], img_path + "/" + record["anonymizedImageFile"])
            size = os.path.getsize(img_path + "/" + record["anonymizedImageFile"])
            tran.Image.find_and_modify({"_id": record["_id"]}, {'$set': {'size': size}})
        db.close()
        return result, 200


@ns.route('/label')
class MetadataLabel(Resource):
    def post(self):
        frm = request.form
        ids = frm.getlist('id[]')
        segment_type = frm['segmentType']
        label = frm.get('label')

        # loop ids, update segmentCharacteristics by record id
        for _id in ids:
            tran.Image.find_and_modify({"_id": _id}, {
                "$set": {
                    'segmentCharacteristics':{
                        'segmentType': segment_type,
                        'label': label
                    }
                }
            })
        total = tran.Image.find().count()
        non_text = tran.Image.find({'segmentCharacteristics.segmentType': 'nonText'}).count()
        multi_line = tran.Image.find({'segmentCharacteristics.segmentType': 'multiLine'}).count()
        word = tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).count()
        words = tran.Image.find({'segmentCharacteristics.segmentType': 'words'}).count()
        partial_word = tran.Image.find({'segmentCharacteristics.segmentType': 'partialWord'}).count()
        result = {
            "success": True,
            "message": "key Feature of " + str(len(ids)) + " records was updated as " + segment_type + " successfully.",
            "stat": "total({0}), word({1}), partial word({2}), multiple lines({3}), not a word({4}), words({5})"
                .format(total, word, partial_word, multi_line, non_text, words)
        }
        return result, 200


@ns.route('/keyFeature')
class MetadataStatus(Resource):
    def post(self):
        frm = request.form
        record = tran.Image.find_and_modify({'img': frm.get('img')}, {
            "$set": {
                'keyFeature': frm.get('keyFeature')
            }
        })

        return dumps(record), 200


@ns.route('/query')
class MetadataQuery(Resource):
    def __get_condition(self, field, frm):
        condition = None
        min_field = 'min' + field
        max_field = 'max' + field
        if frm[min_field] != '' or frm[max_field] != '':
            condition = {}
            if frm[min_field] != '':
                condition['$gte'] = float(frm[min_field])
            if frm[max_field] != '':
                condition['$lte'] = float(frm[max_field])
        return condition

    def post(self):
        frm = request.form
        condition = {}
        fields = ('width', 'height', 'size')
        for field in fields:
            field_condition = self.__get_condition(field, frm)
            if field_condition is not None:
                condition[field] = field_condition

        num = int(frm['num'])
        total = tran.Image.find().count()
        non_text = tran.Image.find({'segmentCharacteristics.segmentType': 'nonText'}).count()
        multi_line = tran.Image.find({'segmentCharacteristics.segmentType': 'multiline'}).count()
        word = tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).count()
        words = tran.Image.find({'segmentCharacteristics.segmentType': 'words'}).count()
        partial_word = tran.Image.find({'segmentCharacteristics.segmentType': 'partialWord'}).count()
        records = tran.Image.find(condition).limit(num)
        db.close()
        result = {
            "total": total,
            "data": loads(dumps(records)),
            "stat": "total({0}), word({1}), partial word({2}), multiple lines({3}), not a word({4}), words({5})"
                .format(total, word, partial_word, multi_line, non_text, words)
        }
        return result, 200

