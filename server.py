import os
from datetime import datetime

from flask import Flask, request
from pymongo import MongoClient

from common import CHAT_USER_HEADER

# TODO global vars
mongo_client = MongoClient(os.environ.get('MONGODB_URL'))
database = mongo_client['chat']
message_collection = database['messages']

app = Flask(__name__)


def fetch_messages():
    return message_collection.find({}, {'_id': False})


def get_user():
    return request.headers.get(CHAT_USER_HEADER)


def get_db_messages(db):
    return db['messages']


@app.get('/messages')
def get_messages():
    try:
        since = float(request.args.get('since', 0))
    except ValueError:
        since = 0

    room = request.args.get('room')
    if not room:
        return {'error': 'missing room parameter'}, 400

    messages = fetch_messages()

    # TODO use mongo query
    return [m for m in messages if m['timestamp'] > since and m['room'] == room]


def persist_message(user, timestamp, message_text, room):
    message_collection.insert_one({'user': user, 'timestamp': timestamp, 'message': message_text, 'room': room})


@app.post('/messages')
def send_message():
    user = get_user()
    if not user:
        return {'error': f'Missing username header ({CHAT_USER_HEADER})'}, 400

    message_text = request.json.get('message')
    if not message_text:
        return {'error': 'Missing message field'}, 400

    room = request.json.get('room')
    if not room:
        return {'error': 'Missing room name'}, 400

    timestamp = datetime.now().timestamp()
    persist_message(user, timestamp, message_text, room)
    return {'success': True}, 201
