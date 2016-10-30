# -*- coding: utf-8 -*-

from flask import Flask
from mongokit import Connection
# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# 实例化Flask框架
app = Flask(__name__)
db = Connection(MONGODB_HOST,MONGODB_PORT)