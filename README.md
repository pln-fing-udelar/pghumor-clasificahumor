# pgHumor-clasificahumor

Web page for [pgHumor](https://github.com/pln-fing-udelar/pghumor) and [HUMOR](https://github.com/pln-fing-udelar/humor) corpora crowd-annotation.

## Setup with Docker

This is useful for production mostly.

1. Create a `docker.env` file with the following content (setting the env vars values):

    ```
    FLASK_SECRET_KEY=SET_VALUE
    MYSQL_ROOT_PASSWORD=SET_VALUE
    ```

2. You should create the database schema as well, and perhaps populate it with data. There's [a sample dump](dump.sql).

3. Then run:

    ```shell
    docker-compose up -d --build
    ```

## Development

This intended to run Flask in debug mode, auto-detecting changes.

1. First install the dependencies using [pipenv](https://docs.pipenv.org/) and start its shell:
    
    ```shell
    pipenv install
    pipenv shell
    ```
    
2. Setup a MySQL database, create the schema and maybe populate it with data.
    
3. Create a `.env` file with the following content (setting some env vars values):
    
    ```
    FLASK_SECRET_KEY=SET_VALUE
    MYSQL_ROOT_PASSWORD=SET_VALUE
    
    FLASK_APP=app/main.py
    FLASK_DEBUG=1
    DB_HOST=SET_VALUE
    DB_USER=SET_VALUE
    DB_NAME=SET_VALUE
    ```
    
4. Run:
    
    ```shell
    flask run
    ```
