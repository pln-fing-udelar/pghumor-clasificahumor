# pgHumor-clasificahumor

Website to crowd-annotate tweets for Humor Research. Originally created for
[pgHumor](https://github.com/pln-fing-udelar/pghumor), and also used in the
[HAHA competitions](http://www.fing.edu.uy/inco/grupos/pln/haha). If you want to learn general information about the 
data and its format, see [HUMOR](https://github.com/pln-fing-udelar/humor) website.

## Setup

There are two ways to run this code after cloning the repo: with Docker or via Pipenv. The first one is the recommended
way to get started (or to just use for the database), and the second one is for the extraction and analysis part, and
for advanced usage (such as debugging with an IDE).

### Docker

You need Docker and Docker Compose for this. To run the Flask development server in debug mode, auto-detecting changes:

```bash
docker-compose up --build
```

### Pipenv

1. (for the tweet extraction part) Install the MySQL library headers. In Ubuntu, it'd be:

    ```bash
    sudo apt install libmysqlclient-dev
    ```

2. Install the dependencies using [Pipenv](https://docs.pipenv.org/):

    ```bash
    pipenv install -d
    ```

3. Create a `.env` file with the following content (setting some env vars values):

    ```shell
    FLASK_APP=clasificahumor/main.py
    FLASK_DEBUG=1
    FLASK_SECRET_KEY=SET_VALUE
    DB_HOST=SET_VALUE
    DB_USER=SET_VALUE
    DB_PASS=SET_VALUE
    DB_NAME=SET_VALUE
    ```

4. Run:

    ```bash
    pipenv shell  # It will load the environment, along with the .env file.
    flask run
    ```

5. Set up a MySQL 5.7 instance. It could be the instance generated with the Docker setup.

## Tweet data

You need a data to mess with.
There's [a dump with the downloaded tweets in the HUMOR repo](https://github.com/pln-fing-udelar/humor/blob/master/extraction/dump-tweets-without-votes.sql).

First, create a database with the options `DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci`. It could be created
with [schema.sql](schema.sql):

```bash
mysql -u $USER -p < schema.sql
```

The default user for Docker is `root`. The default password for the dev environment in Docker is specified in
the [`docker-compose.override.yml`](docker-compose.override.yml) file.

To load a database dump, run in another shell:

```bash
mysql -u $USER -p pghumor < dump.sql
```

You can prefix `docker-compose exec database` to the command to run it in the database Docker container. Or you can use
a local `mysql`:

```bash
# First check the IP address of the container.
# Note the actual Docker container name depends on the local folder name.
docker container inspect pghumor-clasificahumor_database_1 | grep IPAddress
# Then use the IP address (e.g., 172.19.0.3) to connect:
mysql -h 172.19.0.3 -u root -p
# You can also set the password in the command like: -p$PASSWORD
```

**Pro tip:** you can use `mycli`, which is included in the dev dependencies for this project, and it's a more powerful
MySQL default CLI client (e.g., it has code highlighting, command auto-complete, and doesn't need the semicolon at 
the end of every command):

```bash
mycli -h 172.19.0.3 -u root
# You can also set the password in the command like: -p $PASSWORD
```

For both `mysql` and `mycli`, you can append a database name at the end of the command (e.g., `pghumor`) to select it
when starting the session.

### Useful SQL commands

List the databases:

```sql
SHOW DATABASES;
```

List `pghumor` database tables:

```sql
USE pghumor;
SHOW tables;
```

Describe a particular table (e.g., `tweets`):

```sql
DESCRIBE tweets;
```

Show some data from a table:

```sql
SELECT * FROM tweets LIMIT 10;
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

To back up the data in production:

```bash
docker exec clasificahumor_database_1 mysqldump -u root -p pghumor > dump.sql
```

To run a SQL script in production (e.g., to restore some data):

```bash
docker exec -i clasificahumor_database_1 mysql -u root -p pghumor < dump.sql
```

To open a mysql interactive session in production:

```bash
docker exec -i clasificahumor_database_1 mysql -u root -p pghumor
```

For these commands, using directly Docker Compose (`docker-compose exec database`) is also supported instead of the
Docker CLI directly (`docker exec clasificahumor_database_1`). However, the extra flags needed for each of them change
as Docker Compose `exec` subcommand uses a pseudo TTY and it's interactive by default while the Docker CLI `exec`
subcommand doesn't.

## Production setup

The repo was first cloned in production in `/opt/clasificahumor`. The following command was run:

```bash
git config receive.denyCurrentBranch updateInstead
```

The file `/opt/clasificahumor/.git/hooks/post-update` in production has been set with the following content to 
deploy on `git push`:

```bash
#!/usr/bin/env bash

pushd .. > /dev/null  # So it loads the .env file in the working directory.
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
popd > /dev/null
```

## Deploy to production

Add a git remote to push to production:

```bash
git remote add production $YOUR_USERNAME@clasificahumor.com:/opt/clasificahumor
```

Then just push to production:

```bash
git push production
```

## Tweet extraction

Follow the steps here to download new tweets and get them into the database.

### Download new tweets

Add the following to the `.env` file with the content (replace with the Twitter API credentials values):

```shell
CONSUMER_TOKEN=...
CONSUMER_SECRET=...
ACCESS_TOKEN=...
ACCESS_TOKEN_SECRET=...
```

Note that normally we wouldn't need the access token and access token secret as we're not authenticating other users 
to this "Twitter app". However, the app access token can be used to act in name of the Twitter app user owner 
(user-based authentication), and thus gain greater Twitter API rate limits than in an app-based authentication context. 

#### Download tweets from the hose

```bash
./extraction/download_hose.py > tweets1.jsonl
```

#### Download tweets from humorous accounts

```bash
./extraction/download_from_accounts.py > tweets2.jsonl
```

### Persist the downloaded tweets into the database

```bash
./extraction/persist.py < tweets.jsonl
```

See the options available in the command with `./extraction/persist.py --help`.

## Analysis

To compute the agreement (for example with
[this annotations_by_tweet.csv file](https://github.com/pln-fing-udelar/humor/blob/main/annotations_by_tweet.csv)):

```bash
./analysis/agreement.py FILE
```

## Troubleshooting

If you have an SSL connection error when trying to access the database, see
[MySQL ERROR 2026 - SSL connection error - Ubuntu 20.04](https://stackoverflow.com/a/61934186/1165181).
