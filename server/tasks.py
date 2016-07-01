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


def send_report():
    db = get_db()
    seven_days = datetime.now(tzutc()) - timedelta(days=7)
    api_key = os.environ['MAILGUN_KEY']
    mailto = os.environ['MAILTO_REPORT']

    cursor = db.dares.find({'created': {'$gt': seven_days}})
    if not cursor.count():
        return

    output = io.BytesIO()
    output.name = 'report.csv'
    writer = csv.writer(output)
    keys = ['created', 'name', 'email', 'method', 'public', 'dare']
    writer.writerow(keys)

    for doc in cursor:
        writer.writerow([doc[key] for key in keys])

    output.seek(0)

    data = {
        'from': 'noreply@daretolisten.org',
        'to': mailto,
        'subject': 'Dare to Listen Contact Form Messages',
        'text': 'Attached is the weekly dare report as a CSV (Excel) file.'
    }

    resp = requests.post(
        URL, auth=('api', api_key), files=[('attachment', output)], data=data
    )
    print resp
