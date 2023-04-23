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


@click.group()
def cli():
    pass


@click.command()
@click.option('--user', prompt='Username')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
@click.option('--room', prompt='Room name')
def start(user, password, server, room):
    asyncio.run(start_client(user, password, room, server))


@click.command()
@click.option('--user', prompt='Username')
@click.option('--password', prompt=True, hide_input=True)
@click.option('--server', default='http://localhost:5000', help='Chat server endpoint')
def register(user, password, server):
    asyncio.run(register_user(user, password, server))


async def register_user(user, password, server):
    await sio.connect(server)

    success, error = await sio.call('register', data={'user': user, 'password': password})
    if success:
        print('Registration successful')
    else:
        print('Registration failed. Error:', error)

    await sio.disconnect()


async def start_client(user, password, room, server):
    try:
        await sio.connect(server, auth=(user, password))
        await join_room(user, room)
    except Exception as e:
        print('Failed to connect:', e)


cli.add_command(start)
cli.add_command(register)

if __name__ == '__main__':
    cli()
