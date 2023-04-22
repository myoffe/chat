from datetime import datetime

import eventlet
import socketio

import db
from auth import authenticate, register_user

sio = socketio.Server()
app = socketio.WSGIApp(sio)


def push_messages(messages, room, skip_sid=None):
    sio.emit('new_messages', data=messages, room=room, skip_sid=skip_sid)


@sio.event
def send_message(sid, data):
    user = data.get('user')
    if not user:
        return False, 'missing user in request'

    message_text = data.get('message')
    if not message_text:
        return False, 'missing message text'

    timestamp = datetime.now().timestamp()
    room = get_room(sid)
    msg = db.persist_message(user, timestamp, message_text, room)
    push_messages([msg], room, skip_sid=sid)
    return True, ''


def get_room(sid):
    return [room for room in sio.rooms(sid) if room != sid].pop()


@sio.event
def enter_room(sid, data):
    room = data.get('room')
    if not room:
        return 'missing room name'

    print(f'Client {sid} entering room #{room}')
    sio.enter_room(sid, room)

    messages = db.fetch_messages(room)

    # Send all previous messages in room to client
    push_messages(messages, sid)


@sio.event
def register(sid, data):
    username = data.get('user')
    password = data.get('password')
    if None in [username, password]:
        return False, 'Missing parameters'

    return register_user(sid, username, password)


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
