# -*- coding: utf-8 -*-

from flask import Flask
from mongokit import Connection
# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_USER = "transcriptionUser"
DB_PASSWORD = "CLTrans0ptACI"

# 实例化Flask框架
app = Flask(__name__)
db = Connection(MONGODB_HOST,MONGODB_PORT)
db.CLACITranscription.authenticate(DB_USER, DB_PASSWORD)
tran = db.CLACITranscription