# -*- coding: utf-8 -*-
from flask import request
from flask_restplus import Resource
from app.api.models.image import Image
from app.api.metadata import api
from app import db, tran, REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD
from bson.json_util import dumps, loads
import os
import ssh
import csv

ns = api.namespace('metadata', description='Operations related to metadata')


# visit saab server to add file size of each image
@ns.route('/dbremote')
class MetadataWriter(Resource):
    def get(self):
        img_path = "app/static/metadata"
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        remote_img_path = "/export/CSH/projects/word_extraction/anonymized_words/"
        # via ssh, to visit the remote server(saab) to download the metadata image
        client = ssh.SSHClient()
        client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        client.connect(REMOTE_HOST, port=22, username=REMOTE_USER, password=REMOTE_PASSWORD)
        sftp = client.open_sftp()

        # read 5000 images in saab server
        records = tran.Image.find().limit(5000)
        result = {"success": True,
                  "message": "the size of " + str(records.count()) + " records updated successfully"}
        for record in records:
            if not os.path.exists(img_path + "/" + record["anonymizedImageFile"]):
                # download images on saab server to local environment via sftp
                sftp.get(remote_img_path + record["anonymizedImageFile"], img_path + "/" + record["anonymizedImageFile"])
                # get size of each image by getsize() function
                size = os.path.getsize(img_path + "/" + record["anonymizedImageFile"])
                # update image size on saab server according to image unique id
                tran.Image.find_and_modify({"_id": record["_id"]}, {'$set': {'size': size}})
        db.close()
        return result, 200


# from local server to add file size of each image
@ns.route('/db')
class MetadataWriter(Resource):
    def get(self):
        img_path = "app/static/metadata"
        if not os.path.exists(img_path):
            os.makedirs(img_path)

        # read 5000 images in saab server
        records = tran.Image.find().limit(5000)
        result = {"success": True,
                  "message": "the size of " + str(records.count()) + " records updated successfully"}
        for record in records:
                # get size of each image by getsize() function
                size = os.path.getsize(img_path + "/" + record["anonymizedImageFile"])
                # update image size on saab server according to image unique id
                tran.Image.find_and_modify({"_id": record["_id"]}, {'$set': {'size': size}})
        db.close()
        return result, 200


# update segmentCharacteristics property in saab server and get the segmentType statistic
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
        # count the number of images with none text, multiple lines, single word and words
        total = tran.Image.find().count()
        non_text = tran.Image.find({'segmentCharacteristics.segmentType': 'nonText'}).count()
        multi_line = tran.Image.find({'segmentCharacteristics.segmentType': 'multiLine'}).count()
        word = tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).count()
        words = tran.Image.find({'segmentCharacteristics.segmentType': 'words'}).count()
        partial_word = tran.Image.find({'segmentCharacteristics.segmentType': 'partialWord'}).count()
        distinct_word = len(tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).distinct('segmentCharacteristics.label'))
        result = {
            "success": True,
            "message": "key Feature of " + str(len(ids)) + " records was updated as " + segment_type + " successfully.",
            "stat": "total({0}), word({1}), "
                    "distinct_word({6}), partial word({2}), multiple lines({3}), not a word({4}), words({5})"
                .format(total, word, partial_word, multi_line, non_text, words, distinct_word)
        }
        return result, 200


# generate MongoDB queries according to condition user enters and return the results
@ns.route('/query')
class MetadataQuery(Resource):
    # generate the condition according to min and max of height, width and size
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
        # generate query condition
        for field in fields:
            field_condition = self.__get_condition(field, frm)
            if field_condition is not None:
                condition[field] = field_condition

        num = int(frm['num'])
        total = tran.Image.find().count()
        non_text = tran.Image.find({'segmentCharacteristics.segmentType': 'nonText'}).count()
        multi_line = tran.Image.find({'segmentCharacteristics.segmentType': 'multiLine'}).count()
        word = tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).count()
        words = tran.Image.find({'segmentCharacteristics.segmentType': 'words'}).count()
        partial_word = tran.Image.find({'segmentCharacteristics.segmentType': 'partialWord'}).count()
        distinct_word = len(
            tran.Image.find({'segmentCharacteristics.segmentType': 'word'}).distinct('segmentCharacteristics.label'))
        # get matched records
        records = tran.Image.find(condition).limit(num)
        db.close()
        result = {
            "total": total,
            "data": loads(dumps(records)),
            "stat": "total({0}), word({1}), "
                    "distinct_word({6}), partial word({2}), multiple lines({3}), not a word({4}), words({5})"
                .format(total, word, partial_word, multi_line, non_text, words, distinct_word)
        }
        return result, 200


@ns.route('/export')
class MetadataExport(Resource):
    def get(self):
        images = tran.Image.find({"segmentCharacteristics.segmentType": "word"})
        writer = csv.writer(file("app/static/export.csv", "wb"))
        for image in images:
            writer.writerow([image.anonymizedImageFile, image.segmentCharacteristics.label])

        result = {
            "success": True,
            "url": "http://localhost:5000/static/export.csv"
        }
        return result, 200
