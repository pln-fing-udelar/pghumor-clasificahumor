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

```bash
docker-compose up --build
```

### Pipenv

1. Install the dependencies using [pipenv](https://docs.pipenv.org/):

    ```bash
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

    ```bash
    pipenv shell  # It will load the environment, along with the .env file.
    flask run
    ```

4. Setup a MySQL 5.7 instance. It could be the
instance generated with the Docker setup.

## Tweets data

You need a data to mess with.
There's [a dump with the downloaded tweets in the HUMOR
repo](https://github.com/pln-fing-udelar/humor/blob/master/extraction/dump-tweets-without-votes.sql).

First, create a database with the options
`DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci`. It could be
created with [schema.sql](schema.sql):

```bash
mysql -u $USER -p < schema.sql
```

To load a database dump, run in another shell:

```bash
mysql -u $USER -p database < dump.sql
```

You can prefix `docker-compose exec database` to the command to run it
in the database Docker container.

### Useful SQL commands

List the databases:

```sql
show databases;
```

List `pghumor` database tables:

```sql
use pghumor;
show tables;
```

Describe a particular table:

```sql
describe tweets;
```

Show some data from a table:

```sql
select * from tweets limit 10;
```

## Testing

To run it using a WSGI server, just like in production, do:

```bash
docker-compose -f docker-compose.yml -f docker-compose.testing.yml up -d --build
```

Then you can do some testing, such as running a load test:

```bash
./load_test.sh
```

## Manipulating production data

To backup data in production:

```bash
docker exec clasificahumor_database_1 mysqldump -u root -p pghumor > dump.sql
```

To run a SQL script in production (e.g., to restore some data):

```bash
docker exec -i clasificahumor_database_1 mysql -u root -p pghumor < dump.sql
```

To open a mysql interactive session in productrion:

```bash
docker exec -i clasificahumor_database_1 mysql -u root -p pghumor
```

For these commands, using directly Docker Compose (`docker-compose exec database`) is also supported instead of the Docker CLI directly (`docker exec clasificahumor_database_1`). However, the extra flags needed for each of them change as Docker Compose `exec` subcommand uses a pseudo TTY and it's interactive by default while the Docker CLI `exec` subcommand doesn't.
