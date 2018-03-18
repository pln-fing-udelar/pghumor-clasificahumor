# pgHumor-clasificahumor

Web page for [pgHumor](https://github.com/pln-fing-udelar/pghumor) and
[HUMOR](https://github.com/pln-fing-udelar/humor) corpora
crowd-annotation. This is the input data for the
[HAHA](http://www.fing.edu.uy/inco/grupos/pln/haha) competition as well.

## Setup

There are two ways to run this code after cloning the repo: with Docker
or via pipenv. The first one is the recommended way to get started and
the second one is for advanced use (such as debugging with an IDE).

### Docker way

You need Docker and Docker Compose for this. To run the Flask
development server in debug mode, auto-detecting changes:

```shell
docker-compose --build
```

### Pipenv

1. Install the dependencies using [pipenv](https://docs.pipenv.org/):

    ```shell
    pipenv install
    ```

2. Create a `.env` file with the following content (setting some env
vars values):

    ```
    FLASK_APP=clasificahumor/main.py
    FLASK_DEBUG=1
    FLASK_SECRET_KEY=SET_VALUE
    DB_HOST=SET_VALUE
    DB_USER=SET_VALUE
    DB_PASS=SET_VALUE
    DB_NAME=SET_VALUE
    ```

3. Run:

    ```shell
    pipenv shell  # It will load the environment, along with the .env file.
    flask run
    ```

4. Setup a MySQL instance and create a database. It could be the
instance generated with the Docker setup.


## Tweets data

You need a data to mess with.
There's [a dump with the downloaded tweets in the HUMOR
repo](https://github.com/pln-fing-udelar/humor/blob/master/extraction/dump.sql).
To load a database dump, run in another shell:

```shell
mysql -u $USER -p database < dump.sql
```

You can prefix `docker-compose exec database` to the command to run it
in the database Docker container.

## Testing

To run it using a WSGI server, just like in production, do:

```shell
docker-compose -f docker-compose.yml -f docker-compose.testing.yml up -d --build
```

Then you can do some testing, such as running a load test:

```shell
./load_test.sh
```
