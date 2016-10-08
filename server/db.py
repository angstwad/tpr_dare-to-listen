# -*- coding: utf-8 -*-
import os

from pymongo import uri_parser, MongoClient


def get_db():
    mongo_uri = os.environ['MONGO_URI']
    database = uri_parser.parse_uri(mongo_uri)['database']
    return MongoClient(mongo_uri, tz_aware=True)[database]
