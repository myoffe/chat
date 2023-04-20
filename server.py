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
    message = request.get_json()['message']
    time = datetime.now().timestamp()
    messages.append({'user': user, 'time': time, 'message': message})
    return Response(status=201)
