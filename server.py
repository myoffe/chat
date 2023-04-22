from datetime import datetime

from flask import Flask, request

from common import CHAT_USER_HEADER

app = Flask(__name__)

messages = []


def get_user():
    return request.headers.get(CHAT_USER_HEADER)


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
        return {'error': f'Missing username header ({CHAT_USER_HEADER})'}, 400

    message = request.json.get('message', None)
    if not message:
        return {'error': 'Missing message field'}, 400

    timestamp = datetime.now().timestamp()
    messages.append({'user': user, 'timestamp': timestamp, 'message': message})
    return {'success': True}, 201
