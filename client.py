import json
from datetime import datetime
from operator import itemgetter

import click
import requests


def format_msg(msg):
    message, timestamp, user = itemgetter('message', 'timestamp', 'user')(msg)
    time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return f'[{time_str}] {user}: {message}'


def print_messages(messages):
    for msg in messages:
        print(format_msg(msg))


@click.command()
@click.option('--user', prompt='Username')
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
def main(user, server):
    now = datetime.now().timestamp()
    messages = requests.get(f'{server}/messages').json()
    print_messages(messages)


if __name__ == '__main__':
    main()
