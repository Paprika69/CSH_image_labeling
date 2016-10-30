# -*- coding: utf-8 -*-


from mongokit import Document


class Image(Document):
    __collection__="images"
    structure = {
        'img': str,
        'size': int,
        'label': str,
        'width': int,
        'height': int,
        'ratio': float,
        'status': str
    }
    use_dot_notation = True

