import bcrypt

import db


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))


def authenticate(auth):
    user, password = auth
    user = db.fetch_user(user)
    if not user:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), user.get('password'))


def register_user(sid, username, password):
    user = db.fetch_user(username)
    if user:
        return False, 'User already exists'
    print(f'Client {sid} wants to register with usersname {username}')
    password_hash = hash_password(password)
    db.add_user(username, password_hash)
    print(f'Registered user {username}')
    return True, ''
