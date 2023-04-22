# Build this from the top level project directory

FROM python:3.9-slim-buster

RUN pip install "poetry==1.4.2"
WORKDIR /app

# cache deps
COPY poetry.lock pyproject.toml /app/
RUN poetry install

COPY . /app

ENV FLASK_APP=server.py
ENV FLASK_ENV=development

CMD [ "poetry", "run", "python", "server.py"]
EXPOSE 5000