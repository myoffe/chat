from flask import Flask, request, Response
from datetime import datetime

app = Flask(__name__)

messages = []


def get_user():
    return request.headers.get('X-Chat-User')


@app.get('/messages')
def get_messages():
    return messages


@app.post('/messages')
def send_message():
    user = get_user()
    if not user:
        return {'error': 'Missing username header (X-Chat-User)'}, 400

    message = request.get_json().get('message', None)
    if not message:
        return {'error': 'Missing message field'}, 400

    time = datetime.now().timestamp()
    messages.append({'user': user, 'time': time, 'message': message})
    return {'success': True}, 201
