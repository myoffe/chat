import threading
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
    fetch_messages_loop(server, since=0)


def fetch_messages_loop(server, since):
    messages = requests.get(f'{server}/messages?since={since}').json()
    last_fetched_at = datetime.now().timestamp()

    print_messages(messages)

    threading.Timer(1, fetch_messages_loop, [server, last_fetched_at]).start()


if __name__ == '__main__':
    main()
