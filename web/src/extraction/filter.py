#!/usr/bin/env python
import argparse
import random
from typing import Iterable, Mapping, Set, Tuple

import util
from argparse_with_defaults import ArgumentParserWithDefaults

LIMIT = 4500


def tweets_with_unique_text(tweets: Iterable[util.TYPE_TWEET]) -> Iterable[util.TYPE_TWEET]:
    return {tweet["text"]: tweet for tweet in tweets}.values()


def tweets_from_database() -> Tuple[Mapping[str, util.TYPE_TWEET], Set[str]]:
    with util.create_connection() as connection, connection as cursor:
        cursor.execute("SELECT tweet_id, text FROM tweets")
        tweets = {id_: text for id_, text in cursor.fetchall()}
        return tweets, set(tweets.values())


def parse_args() -> argparse.Namespace:
    parser = ArgumentParserWithDefaults()
    parser.add_argument("path", metavar="FILE", nargs="?", default="-")
    parser.add_argument("--no-json-format", dest="json_format", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_tweets = util.read_tweets_from_input(args.path, args.json_format)
    input_tweets = list(tweets_with_unique_text(input_tweets))

    db_tweets_by_id, db_tweet_texts = tweets_from_database()

    tweets_to_consider = []

    for input_tweet in input_tweets:
        db_tweet_text = db_tweets_by_id.get(input_tweet["id"])
        if db_tweet_text:
            assert input_tweet["text"] == db_tweet_text

        if not db_tweet_text and input_tweet["text"] not in db_tweet_texts:
            tweets_to_consider.append(input_tweet)

    for tweet in random.sample(tweets_to_consider, LIMIT):
        print(util.serialize_tweet(tweet) if args.json_format else tweet)


if __name__ == "__main__":
    main()
