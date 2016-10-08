# -*- coding: utf-8 -*-
import random
from datetime import datetime

from dateutil.tz import tzutc
from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser

import choices
from db import get_db
from utils import boolify, two_oh_one
from reports import opt_in_email_report, opt_out_email_report


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


class ReportResource(Resource):
    """
    /reports
    """
    report_names = {
        'email_opt_in': "Opt-In Email Report",
        'email_opt_out': "Opt-Out Email Report",
    }
    report_map = {
        'email_opt_in': opt_in_email_report,
        'email_opt_out': opt_out_email_report,
    }

    def validate_post(self):
        parser = RequestParser()
        parser.add_argument('report', required=True)
        parser.add_argument('email', required=True)
        return parser.parse_args()

    def get(self):
        return self.report_names

    def post(self):
        args = self.validate_post()
        args.email = args.email.strip().lower()
        try:
            assert args.report in self.report_names, "not valid report"
            assert (args.email == 'pauldurivage@gmail.com' or
                    args.email.endswith('@tpr.org')), "invalid email"
        except AssertionError as e:
            abort(400, message=e.message)

        self.report_map[args.report](args.email)
        return two_oh_one()
