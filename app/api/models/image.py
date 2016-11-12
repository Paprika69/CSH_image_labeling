# -*- coding: utf-8 -*-


from mongokit import Document


class Image(Document):
    __collection__="meetingMinuteWords"
    structure = {
        'locationBasedImageFile': str,
        'numPage': int,
        'locationY': int,
        'locationX': int,
        'numLine': int,
        'numWord': int,
        'register': int,
        'anonymizedImageFile': str,
        'recordType': int,
        'width': int,
        'height': int,
        'size': int,

        'segmentCharacteristics':{
            'segmentType': str,
            'label': str
        }
    }
    use_dot_notation = True

