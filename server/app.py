# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime

from dateutil.tz import tzutc
from flask import Flask, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient, uri_parser
from flask_restful.reqparse import RequestParser

import choices


def get_db():
    mongo_uri = os.environ['MONGO_URI']
    database = uri_parser.parse_uri(mongo_uri)['database']
    return MongoClient(mongo_uri, tz_aware=True)[database]


def two_oh_one():
    resp = make_response()
    resp.status_code = 201
    return resp


def boolify(value):
    if value is None:
        return True
    if value.lower() == 'true':
        return True
    return False


class DareResource(Resource):
    """
    /dare
    """
    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('dare', choices=choices.VALID_DARES, required=True)
        parser.add_argument('method', default='tpr')
        parser.add_argument('public')
        parser.add_argument('optIn', required=True)
        return parser.parse_args()

    def post(self):
        args = self.validate_post()

        if args.method == 'facebook' or args.method == 'twitter':
            args.public = False
        else:
            args.public = boolify(args.get('public'))

        args.optIn = boolify(args.get('optIn'))

        args.created = datetime.now(tz=tzutc())

        db = get_db()
        db.dares.insert_one(args)

        return two_oh_one()


class ContactFormResource(Resource):
    """
    /contact
    """
    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('message', required=True)
        return parser.parse_args()

    def post(self):
        args = self.validate_post()
        args.created = datetime.now(tz=tzutc())
        db = get_db()
        db.messages.insert_one(args)
        return two_oh_one()


class DareCountResource(Resource):
    """
    /dare-count
    """
    def get(self):
        db = get_db()
        count = len(db.dares.distinct('email'))
        return {'count': count}


class PublicTprDaresResource(Resource):
    """
    /dares
    """
    def get(self):
        db = get_db()
        docs = list(
            db.dares.find(
                {
                    'method': 'tpr',
                    'public': True,
                },
                sort=(('_id', -1),),
                limit=100
            )
        )

        dares = []
        if docs:
            for x in xrange(4):
                dares.append(random.choice(docs))
            dares = [dict(y) for y in set(tuple(x.items()) for x in dares)]

        processed = []
        for dare in dares:
            name_list = dare['name'].title().split()
            if len(name_list) is 1:
                namestr = "%s." % name_list[0]
            elif len(name_list) >= 2:
                namestr = "%s %s." % (name_list[0], name_list[-1][:1])
            processed.append({
                'name': namestr,
                'dare': 'I dare to %s.' % dare['dare']
            })

        return {'dares': processed}


app = Flask(__name__)
api = Api(app)
api.add_resource(DareResource, '/dare')
api.add_resource(ContactFormResource, '/contact')
api.add_resource(PublicTprDaresResource, '/dares')
api.add_resource(DareCountResource, '/dare-count')


def main():
    import json
    with open('dev-config.json') as f:
        os.environ.update(json.load(f))
    app.run(debug=True)

if __name__ == '__main__':
    main()
