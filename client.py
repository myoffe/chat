import json
import threading
from datetime import datetime
from operator import itemgetter

import click
import requests

from common import CHAT_USER_HEADER


def format_msg(msg):
    message, timestamp, user = itemgetter('message', 'timestamp', 'user')(msg)
    time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return f'[{time_str}] {user}: {message}'


def print_messages(messages):
    for msg in messages:
        print(format_msg(msg))


def prompt_and_send_messages(user, room, endpoint):
    while True:
        msg = input('[Send message] ')
        if not msg:
            continue
        res = requests.post(endpoint, json={'message': msg, 'room': room}, headers={CHAT_USER_HEADER: user})
        result = res.json()
        if not result.get('success'):
            print('Failed to send message. Error:', result.get('error'))


@click.command()
@click.option('--user', prompt='Username')
@click.option('--room', prompt='Room name')
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
def main(user, room, server):
    endpoint = f'{server}/messages'

    print(f'Room: #{room}')

    fetch_messages_loop(endpoint, room, since=0)
    prompt_and_send_messages(user, room, endpoint)


def fetch_messages_loop(endpoint, room, since):
    messages = requests.get(f'{endpoint}?since={since}&room={room}').json()
    last_fetched_at = datetime.now().timestamp()

    print_messages(messages)

    threading.Timer(1, fetch_messages_loop, [endpoint, room, last_fetched_at]).start()


if __name__ == '__main__':
    main()
