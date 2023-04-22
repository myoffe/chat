import asyncio
from datetime import datetime
from operator import itemgetter

import aioconsole
import click
import socketio

sio = socketio.AsyncClient()


def format_msg(msg):
    message, timestamp, user, room = itemgetter('message', 'timestamp', 'user', 'room')(msg)
    time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    return f'[{time_str}] #{room} | {user}: {message}'


def print_messages(messages):
    for msg in messages:
        print(format_msg(msg))


async def prompt_and_send_messages(user, room):
    while True:
        msg = await aioconsole.ainput(f'#{room} > ')
        if not msg:
            continue

        await sio.emit('send_message', data={'message': msg, 'user': user})


def send_message_callback(error):
    print('Failed to send message. Error:', error)


@click.command()
@click.option('--user', prompt='Username')
@click.option('--room', prompt='Room name')
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
def main(user, room, server):
    asyncio.run(start(user, room, server))


async def start(user, room, server):
    await sio.connect(server)
    await sio.emit('enter_room', data={'room': room})
    await prompt_and_send_messages(user, room)


@sio.event
async def connect():
    print('Connection established')


@sio.event
async def disconnect():
    print('Disconnected from server')


@sio.event
async def new_messages(data):
    print_messages(data)


if __name__ == '__main__':
    main()
