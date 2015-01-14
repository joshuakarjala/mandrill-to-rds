import os
import sys
import datetime
import json
import psycopg2

from psycopg2.extras import Json

from bottle import get, post, run, request
from bottle import jinja2_template as template

# Connection credentials
DB_HOST = os.environ.get('DB_HOST')
if not DB_HOST:
    print >> sys.stderr, 'Missing environment variable DB_HOST'
    exit(1)


DB_NAME = os.environ.get('DB_NAME')
if not DB_NAME:
    print >> sys.stderr, 'Missing environment variable DB_NAME'
    exit(1)


# make sure we have AWS credentials and a S3 Bucket
DB_USER = os.environ.get('DB_USER')
if not DB_USER:
    print >> sys.stderr, 'Missing environment variable DB_USER'
    exit(1)


DB_PASSWORD = os.environ.get('DB_PASSWORD')
if not DB_PASSWORD:
    print >> sys.stderr, 'Missing environment variable DB_PASSWORD'
    exit(1)


TABLE_NAME = os.environ.get('TABLE_NAME')
if not TABLE_NAME:
    print >> sys.stderr, 'Missing environment variable TABLE_NAME'
    exit(1)


def write_to_db(data):
    today = datetime.datetime.now()

    # establish connection to RDS
    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (DB_HOST, DB_NAME, DB_USER, TABLE_NAME))
    cur = conn.cursor()

    cur.execute("insert into %s (jsondata) values (%s)", TABLE_NAME, [Json(data)])

    conn.commit()
    cur.close()
    conn.close()


@post('/inbound_mail')
def inbound_mail():
    post_data = request.POST
    event_list = json.loads(post_data.get('mandrill_events'))

    for data in event_list:
        write_to_db(data)

    return 'OK'


@get('/setup')
def setup():
    url = request.url.replace('/setup', '/inbound_mail')
    return template('This is your hook url, copy it:<h3>{{url}}</h3>', url=url)

run(host='0.0.0.0', port=int(os.environ.get('PORT', 8010)))
