from datetime import datetime

from flask import Flask, request

app = Flask(__name__)

messages = []


def get_user():
    return request.headers.get('X-Chat-User')


@app.get('/messages')
def get_messages():
    try:
        since = float(request.args.get('since', 0))
    except ValueError:
        since = 0

    return [m for m in messages if m['timestamp'] > since]


@app.post('/messages')
def send_message():
    user = get_user()
    if not user:
        return {'error': 'Missing username header (X-Chat-User)'}, 400

    message = request.get_json().get('message', None)
    if not message:
        return {'error': 'Missing message field'}, 400

    timestamp = datetime.now().timestamp()
    messages.append({'user': user, 'timestamp': timestamp, 'message': message})
    return {'success': True}, 201
