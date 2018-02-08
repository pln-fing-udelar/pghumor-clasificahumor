# pgHumor-clasificahumor

Web page for [pgHumor](https://github.com/pln-fing-udelar/pghumor) and [HUMOR](https://github.com/pln-fing-udelar/humor) corpora crowd-annotation.

## Setup

Create a `.env` file with the following content (setting the env vars values):

```
FLASK_SECRET_KEY=SET_VALUE
MYSQL_ROOT_PASSWORD=SET_VALUE
```

You should create the database schema as well, and perhaps populate it with data. There's [a sample dump](chistedump.sql).

Then run:

```shell
docker-compose up -d --build
```

## Development

First, from `app` folder, install the dependencies using [pipenv](https://docs.pipenv.org/):

```shell
pipenv install
pipenv shell
```

Then, to run with the Flask development server (and some MySQL server instance), instance the env vars and run it, like this:

```shell
env FLASK_DEBUG=1 DB_HOST=172.18.0.2 DB_USER=root DB_NAME=chistesdb $(cat ../.env | grep -v ^# | xargs) flask run
```
