# -*- coding: utf-8 -*-

from flask import Flask
from mongokit import Connection

# 实例化Flask框架
app = Flask(__name__)
# read config file
app.config.from_json("config.json")
MONGODB_HOST = app.config["MONGODB_HOST"]
MONGODB_PORT = app.config["MONGODB_PORT"]
DB_USER = app.config["DB_USER"]
DB_PASSWORD = app.config["DB_PASSWORD"]
REMOTE_HOST = app.config["REMOTE_HOST"]
REMOTE_USER = app.config["REMOTE_USER"]
REMOTE_PASSWORD = app.config["REMOTE_PASSWORD"]

db = Connection(MONGODB_HOST, MONGODB_PORT)
db.CLACITranscription.authenticate(DB_USER, DB_PASSWORD)
tran = db.CLACITranscription