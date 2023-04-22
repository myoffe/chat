# Python chat app

## Running with docker

### Server
```
cd <project dir>
docker build . -t chat-server -f docker/server/Dockerfile
docker run -p 5000:5000 chat-server
```

### Client
```
cd <project dir>
docker build . -t chat-client -f docker/client/Dockerfile
docker run chat-client
```

## TODOs
### Functional
- [X] Exclude user's own new messages from message fetching loop
- [ ] Fix text prompt not seen properly after receiving messages
- [X] Clean up debug prints
- [ ] Handle reconnects gracefully

### Non-functional
- [ ] Clean up code TODOs
- [X] Use SocketIO rooms
- [ ] Allow dockerized client to communicate with server
- [ ] Extract common Dockerfile functionality
- [ ] Separate projects or just the dependencies
