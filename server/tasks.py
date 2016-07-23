# -*- coding: utf-8 -*-
import os
import csv
from datetime import datetime, timedelta

import io
import requests
from dateutil.tz import tzutc

from app import get_db


URL = 'https://api.mailgun.net/v3/idaretolisten.org/messages'


def send_contacts():
    db = get_db()
    day_ago = datetime.now(tzutc()) - timedelta(days=1)
    api_key = os.environ['MAILGUN_KEY']
    mailto = os.environ['MAILTO_CONTACT']

    cursor = db.messages.find({'created': {'$gt': day_ago}})
    if not cursor.count():
        return

    body = "Here are the contact emails from the last 24 hours:\n\n"
    for doc in cursor:
        body += (
            "Name: {name}\n"
            "Email: {email}\n"
            "Created: {created}\n"
            "Message:\n{message}\n"
            "----------------------\n\n"
        ).format(**doc)

    data = {
        'from': 'noreply@daretolisten.org',
        'to': mailto,
        'subject': 'Dare to Listen Contact Form Messages',
        'text': body,
    }
    resp = requests.post(URL, auth=('api', api_key), data=data)
    print resp


def get_social_counts_text(db):
    cursor = db.dares.aggregate([
        {
            '$match': {}
        },
        {
            '$group': {
                '_id': '$method',
                'count': {
                    '$sum': 1
                }
            }
        }
    ])
    text = "The total count of dares by platform are as follows:\n"
    for doc in cursor:
        _id = doc['_id']
        method = _id.title() if _id != 'tpr' else 'TPR'
        text += "%s: %s\n" % (method, doc['count'])
    return text


def get_counts_text(db):
    distinct = len(db.dares.distinct('email'))
    total = db.dares.count()
    return """\
Total dares: {total}
Distinct email addresses: {distinct}
""".format(total=total, distinct=distinct)


def get_report(db):
    seven_days = datetime.now(tzutc()) - timedelta(days=7)

    cursor = db.dares.find({'created': {'$gt': seven_days}})
    if not cursor.count():
        return

    output = io.BytesIO()
    output.name = 'report.csv'
    writer = csv.writer(output)
    keys = ['created', 'name', 'email', 'method', 'public', 'optIn', 'dare']
    writer.writerow(keys)

    for doc in cursor:
        items = map(
            lambda x: x.encode('utf-8') if isinstance(x, basestring) else x,
            (doc.get(key) for key in keys)
        )
        writer.writerow(items)

    output.seek(0)
    return output


def send_report():
    db = get_db()
    api_key = os.environ['MAILGUN_KEY']
    mailto = os.environ['MAILTO_REPORT']

    social_counts = get_social_counts_text(db)
    total_counts = get_counts_text(db)

    body = """\
Hello,

This is the weekly rollup report.

{social_counts}

{total_counts}

Please find the attached weekly dares report as a CSV (Excel) file.

Sincerely,
An Anonymous Lambda Function running in the Amazon Cloud
""".format(social_counts=social_counts, total_counts=total_counts)

    report_fobj = get_report(db)

    data = {
        'from': 'idaretolisten.org <noreply@daretolisten.org>',
        'to': mailto,
        'subject': 'Dare to Listen Contact Form Messages',
        'text': body,
    }

    resp = requests.post(
        URL, auth=('api', api_key), files=[('attachment', report_fobj)], data=data
    )
    print resp
