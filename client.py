import asyncio
from datetime import datetime
from operator import itemgetter

import aioconsole
import click
import socketio

sio = socketio.AsyncClient()

MESSAGE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def format_chat_message(msg):
    message, timestamp, user, room = itemgetter('message', 'timestamp', 'user', 'room')(msg)
    time_str = datetime.fromtimestamp(timestamp).strftime(MESSAGE_DATE_FORMAT)
    return f'[{time_str}] #{room} | {user}: {message}'


def print_chat_messages(messages):
    for msg in messages:
        print(format_chat_message(msg))


async def join_room(user, room):
    await sio.emit('enter_room', data={'room': room})
    while True:
        msg = await aioconsole.ainput(f'#{room} > ')
        if not msg:
            # Ignore empty inputs
            continue

        success, error = await sio.call('send_message', data={'message': msg, 'user': user})
        if not success:
            print('Failed to send message. Error:', error)


@sio.event
async def connect():
    print('Connection established')


@sio.event
async def disconnect():
    print('Disconnected from server')


@sio.event
async def new_messages(data):
    print_chat_messages(data)


@click.command()
@click.option('--register', is_flag=True, prompt='Do you want to register?')
@click.option('--user', prompt='Username')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--room', prompt='Room name')
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
def main(register, user, password, room, server):
    asyncio.run(start_client(register, user, password, room, server))


async def start_client(register, user, password, room, server):
    if register:
        await sio.connect(server)
        success, error = await sio.call('register', data={'user': user, 'password': password})
        if not success:
            print('Registration failed. Error:', error)
            return

        print('Registration successful! Please restart client')

    else:
        try:
            await sio.connect(server, auth=(user, password))
            await join_room(user, room)
        except Exception as e:
            print('Failed to connect:', e)


if __name__ == '__main__':
    main()
