from datetime import datetime

import bcrypt
import eventlet
import socketio

import db

sio = socketio.Server()
app = socketio.WSGIApp(sio)


def push_messages(messages, room, skip_sid):
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
    room = [room for room in sio.rooms(sid) if room != sid].pop()
    msg = db.persist_message(user, timestamp, message_text, room)
    push_messages([msg], room, skip_sid=sid)
    return True, ''


@sio.event
def enter_room(sid, data):
    room = data.get('room')
    if not room:
        return 'missing room name'

    print(f'Client {sid} entering room #{room}')
    sio.enter_room(sid, room)

    messages = db.fetch_all_messages_in_room(room)

    # Send all previous messages in room to client
    push_messages(messages, sid, None)


@sio.event
def register(sid, data):
    username = data.get('user')
    password = data.get('password')
    if None in [username, password]:
        return False, 'Missing parameters'

    user = db.fetch_user(username)
    if user:
        return False, 'User already exists'

    print(f'Client {sid} wants to register with usersname {username}')

    password_hash = hash_password(password)
    db.add_user(username, password_hash)
    print(f'Registered user {username}')

    return True, ''


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))


def authenticate(auth):
    user, password = auth
    user = db.fetch_user(user)
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
