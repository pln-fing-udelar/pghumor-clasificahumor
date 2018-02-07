FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN set -ex && pip install pipenv --upgrade

COPY app/Pipfile* /app/

RUN set -ex && pipenv install --deploy --system

COPY app/ /app
