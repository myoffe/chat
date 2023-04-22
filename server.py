import os
from datetime import datetime

import bcrypt
from pymongo import MongoClient

mongo_client = MongoClient(os.environ.get('MONGODB_URL'))
database = mongo_client['chat']
message_collection = database['messages']
users_collection = database['users']

import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)


def fetch_all_messages_in_room(room):
    return list(message_collection.find({'room': room}, {'_id': False}))


def push_messages(messages, room, skip_sid):
    sio.emit('new_messages', data=messages, room=room, skip_sid=skip_sid)


def persist_message(user, timestamp, message_text, room):
    obj = {'user': user, 'timestamp': timestamp, 'message': message_text, 'room': room}
    message_collection.insert_one(obj)
    del obj['_id']
    return obj


@sio.event
def send_message(sid, data):
    user = data.get('user')
    if not user:
        return False, 'missing user in request'

    message_text = data.get('message')
    if not message_text:
        return False, 'missing message text'

    timestamp = datetime.now().timestamp()
    room = [room for room in sio.rooms(sid) if room != sid].pop()
    msg = persist_message(user, timestamp, message_text, room)
    push_messages([msg], room, skip_sid=sid)
    return True, ''


@sio.event
def enter_room(sid, data):
    room = data.get('room')
    if not room:
        return 'missing room name'

    print(f'Client {sid} entering room #{room}')
    sio.enter_room(sid, room)

    messages = fetch_all_messages_in_room(room)

    # Send all previous messages in room to client
    push_messages(messages, sid, None)


@sio.event
def register(sid, data):
    username = data.get('user')
    password = data.get('password')
    if None in [username, password]:
        return False, 'Missing parameters'

    user = users_collection.find_one({'user': username})
    if user:
        return False, 'User already exists'

    print(f'Client {sid} wants to register with usersname {username}')

    password_hash = hash_password(password)
    users_collection.insert_one({'user': username, 'password': password_hash})
    print(f'Registered user {username}')

    return True, ''


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))


def authenticate(auth):
    user, password = auth
    user = users_collection.find_one({'user': user})
    if not user:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), user.get('password'))


@sio.event
def connect(sid, environ, auth):
    print(f'Client {sid} connecting')
    if auth and not authenticate(auth):
        raise ConnectionRefusedError('Authentication failed')

    print(f'Client {sid} authenticated')


@sio.event
def disconnect(sid):
    print(f'Client {sid} disconnected')


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
