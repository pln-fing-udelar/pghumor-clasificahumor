#!/usr/bin/env python
import argparse
from typing import Iterable

import MySQLdb

import util
from argparse_with_defaults import ArgumentParserWithDefaults


def insert_users(connection: MySQLdb.Connection, user_ids: Iterable[str]) -> None:
    with connection.cursor() as cursor:
        cursor.executemany("INSERT INTO accounts (account_id) VALUES (%s)"
                           " ON DUPLICATE KEY UPDATE account_id = account_id;", user_ids)


def insert_tweets(connection: MySQLdb.Connection, tweets: Iterable[util.TYPE_TWEET]) -> None:
    with connection.cursor() as cursor:
        # Consider that there are duplicate tweets in sample sometimes.
        cursor.executemany("INSERT INTO tweets (tweet_id, text, account_id, origin, lang)"
                           " VALUES (%(id)s, %(text)s, %(user_id)s, %(origin)s, %(lang)s)"
                           " ON DUPLICATE KEY UPDATE tweet_id = tweet_id", tweets)


def parse_args() -> argparse.Namespace:
    parser = ArgumentParserWithDefaults()
    parser.add_argument("path", metavar="FILE", nargs="?", default="-")
    parser.add_argument("--default-language", default="es", help="default language of the tweets")
    parser.add_argument("--default-origin", choices=["hose", "humorous account"], help="default origin of the tweets")
    parser.add_argument("--no-json-format", dest="json_format", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tweets = util.read_tweets_from_input(args.path, args.json_format)

    for tweet in tweets:
        tweet.setdefault("lang", args.default_language)
        if args.default_origin:
            tweet.setdefault("origin", args.default_origin)

        # Consider that the key names may vary between "tweet_id" or "id", and `account_id or "user_id",
        # depending on the input file.
        id_ = tweet.get("tweet_id")
        if id_:
            tweet["id"] = id_

        user_id = tweet.get("account_id")
        if user_id:
            tweet["user_id"] = user_id

    with util.create_connection() as connection:
        try:
            insert_users(connection, {tweet.get("account_id", tweet.get("user_id")) for tweet in tweets})
            insert_tweets(connection, tweets)
            connection.commit()
        except Exception:
            connection.rollback()
            raise


if __name__ == "__main__":
    main()
