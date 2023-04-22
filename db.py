import os
from pymongo import MongoClient

mongo_client = MongoClient(os.environ.get('MONGODB_URL'))
database = mongo_client['chat']

messages = database['messages']
users = database['users']


def persist_message(user, timestamp, message_text, room):
    obj = {'user': user, 'timestamp': timestamp, 'message': message_text, 'room': room}
    messages.insert_one(obj)
    del obj['_id']
    return obj


def add_user(username, password_hash):
    users.insert_one({'user': username, 'password': password_hash})


def fetch_user(username):
    return users.find_one({'user': username})


def fetch_all_messages_in_room(room):
    return list(messages.find({'room': room}, {'_id': False}))
