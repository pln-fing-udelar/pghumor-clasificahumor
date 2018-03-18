FROM tiangolo/uwsgi-nginx-flask:python3.6

RUN set -ex && pip install pipenv --upgrade

COPY Pipfile* /app/

RUN set -ex && pipenv install --deploy --system

COPY uwsgi.conf /etc/nginx/conf.d/
COPY uwsgi.ini .
COPY prestart.sh .
COPY clasificahumor clasificahumor
