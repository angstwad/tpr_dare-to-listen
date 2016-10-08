# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api

from resources import DareResource, ContactFormResource, DareCountResource, \
    PublicTprDaresResource, ReportResource


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(DareResource, '/dare')
    api.add_resource(ContactFormResource, '/contact')
    api.add_resource(PublicTprDaresResource, '/dares')
    api.add_resource(DareCountResource, '/dare-count')
    api.add_resource(ReportResource, '/reports')
    return app
