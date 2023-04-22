# Build this from the top level project directory

FROM python:3.9-slim-buster

RUN pip install "poetry==1.4.2"
WORKDIR /app

# cache deps
COPY poetry.lock pyproject.toml /app/
RUN poetry install

COPY . /app

ENTRYPOINT [ "poetry", "run", "python", "client.py"]