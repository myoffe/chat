# Python chat app

## Running

### Server

```
cd <project dir>
docker build . -t chat-server -f docker/server/Dockerfile
docker-compose -f docker/server/docker-compose.yml up
```

### Client

#### Without docker

```
cd <project dir>
poetry run python client.py register
poetry run python client.py start
```

#### With docker (tested only on Mac)

```
docker build . -t chat-client -f docker/client/Dockerfile
docker run -it chat-client register --server http://host.docker.internal:5000
docker run -it chat-client start --server http://host.docker.internal:5000
```

## Notes & Limitations

Sometimes the typing prompt might be obstructed by incoming messages.

You can still type and it will send a message. Or just press Enter to make it visible.

## TODOs

### Functional

- [X] "Event loop is closed" error when finishing registration
- [ ] Informative 'invalid credenentials' error
- [X] Exclude user's own new messages from message fetching loop
- [ ] Fix text prompt not seen properly after receiving messages
- [X] Clean up debug prints
- [ ] Handle reconnects gracefully
- [X] Authentication
- [ ] User seen message functionality
- [ ] Prevent double login?

### Non-functional

- [X] Allow dockerized client to communicate with server
- [X] Clean up code TODOs
- [X] Avoid globals in server.py
- [X] Use SocketIO rooms
- [ ] Extract common Dockerfile functionality
- [ ] Separate projects or just the dependencies
