FROM python:3.10-alpine as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10-alpine

COPY --from=node:alpine /usr/local/bin /usr/local/bin
COPY --from=node:alpine /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm

WORKDIR /code

RUN apk add --no-cache \
    bash \ 
    build-base \
    g++ \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    giflib-dev
COPY ./georender /code/georender
RUN npm install ./georender

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code
CMD ["python", "main.py"]