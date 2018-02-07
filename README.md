# pgHumor-clasificahumor

Web page for [pgHumor](https://github.com/pln-fing-udelar/pghumor) and [HUMOR](https://github.com/pln-fing-udelar/humor) corpora crowd-annotation.

## Setup

Create a `.env` file with the following content (setting the env vars values):

```
FLASK_SECRET_KEY=SET_VALUE
MYSQL_ROOT_PASSWORD=SET_VALUE
```

Then run:

```shell
docker-compose up -d --build
```
