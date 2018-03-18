FROM python:3.6

RUN set -ex && pip install pipenv --upgrade

WORKDIR /usr/src/app

COPY Pipfile* ./

RUN set -ex && pipenv install --deploy --system

COPY clasificahumor clasificahumor

EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]
