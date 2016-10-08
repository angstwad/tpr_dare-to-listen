# -*- coding: utf-8 -*-
import io
import os
import csv

import requests

from db import get_db
from tasks import URL


def opt_in_email_report(email):
    db = get_db()
    api_key = os.environ['MAILGUN_KEY']

    body = """\
Hello,

Attached is the opt-in email report as requested.

Sincerely,
An Anonymous Lambda Function running in the Amazon Cloud
"""

    cur = db.dares.find({
        "$or": [
            {
                "optIn": {
                    "$exists": False
                }
            },
            {
                "optIn": True
            }
        ]},
        sort=[('name', 1)]
    )

    deduped = set()
    output = io.BytesIO()
    output.name = "report.csv"
    writer = csv.writer(output)
    writer.writerow(['name', 'email'])
    for doc in cur:
        deduped.add((
            doc['name'].encode('utf-8').title(),
            doc['email'].encode('utf-8').lower(),
        ))
    for tup in sorted(deduped, key=lambda x: x[0]):
        writer.writerow(tup)
    output.seek(0)

    data = {
        'from': 'idaretolisten.org <noreply@daretolisten.org>',
        'to': email,
        'subject': 'Dare to Listen Email Rollup',
        'text': body,
    }

    resp = requests.post(
        URL, auth=('api', api_key), files=[('attachment', output)],
        data=data
    )
    print resp


def opt_out_email_report(email):
    db = get_db()
    api_key = os.environ['MAILGUN_KEY']

    body = """\
Hello,

Attached is the opt-out email report as requested.

Sincerely,
An Anonymous Lambda Function running in the Amazon Cloud
"""

    cur = db.dares.find({"optIn": False}, sort=[('name', 1)])

    deduped = set()
    output = io.BytesIO()
    output.name = "report.csv"
    writer = csv.writer(output)
    writer.writerow(['name', 'email'])
    for doc in cur:
        deduped.add((
            doc['name'].encode('utf-8').title(),
            doc['email'].encode('utf-8').lower(),
        ))
    for tup in sorted(deduped, key=lambda x: x[0]):
        writer.writerow(tup)
    output.seek(0)

    data = {
        'from': 'idaretolisten.org <noreply@daretolisten.org>',
        'to': email,
        'subject': 'Dare to Listen Email Rollup',
        'text': body,
    }

    resp = requests.post(
        URL, auth=('api', api_key), files=[('attachment', output)],
        data=data
    )
    print resp
