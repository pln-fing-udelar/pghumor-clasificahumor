#!/usr/bin/env python
import argparse
import time

from tqdm.auto import tqdm

import util
from argparse_with_defaults import ArgumentParserWithDefaults

USER_AUTH_STATUSES_LOOKUP_RATE_LIMIT_PER_WINDOW = 900
SECS_IN_A_MINUTE = 60
DELAY_PER_USER_AUTH_STATUSES_LOOKUP_REQUEST = 15 * SECS_IN_A_MINUTE / USER_AUTH_STATUSES_LOOKUP_RATE_LIMIT_PER_WINDOW
MAX_STATUSES_COUNT_PER_STATUSES_LOOKUP = 100


def parse_args() -> argparse.Namespace:
    parser = ArgumentParserWithDefaults()
    parser.add_argument("--cached", help="file with the tweets already downloaded")
    parser.add_argument("--no-json-format", dest="json_format", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with util.create_connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT tweet_id, text FROM tweets")
                tweets_in_db_by_id = {t[0]: {"id": t[0], "text": t[1]} for t in cursor.fetchall()}
                tweets_in_db = list(tweets_in_db_by_id.values())

            if args.cached:
                with open(args.cached) as cached_file:
                    new_tweets = util.read_tweets(cached_file)
            else:
                # Use different lists for the current ones and the new ones so deleted tweets preserve their text in the
                # DB.
                new_tweets = []

                api = util.create_tweepy_api()

                with tqdm(total=len(tweets_in_db), desc="Downloading statuses") as progress_bar:
                    for tweet_group in util.chunks(tweets_in_db, MAX_STATUSES_COUNT_PER_STATUSES_LOOKUP):
                        statuses = api.statuses_lookup((tweet["id"] for tweet in tweet_group), map_=False)
                        new_tweets.extend(util.status_to_dict(status) for status in statuses)
                        time.sleep(DELAY_PER_USER_AUTH_STATUSES_LOOKUP_REQUEST)
                        progress_bar.update(len(tweet_group))

                for tweet in new_tweets:
                    print(util.serialize_tweet(tweet) if args.json_format else tweet)

            tweets_to_update = [tweet
                                for tweet in new_tweets
                                if tweet["text"] != tweets_in_db_by_id[tweet["id"]]["text"]]

            with connection.cursor() as cursor:
                # There is no simple way to do a batch update in MySQL. One option would be to use
                # INSERT ... ON DUPLICATE KEY UPDATE, but it makes compulsory to specify the rest of the fields if not
                # null. Maybe it could have been done with REPLACE.
                for tweet in tweets_to_update:
                    cursor.execute("UPDATE tweets SET text = %(text)s WHERE tweet_id = %(id)s", tweet)

            connection.commit()
        except Exception:
            connection.rollback()
            raise

        # Check that everything is alright.
        with connection.cursor() as cursor:
            cursor.execute("SELECT tweet_id, text FROM tweets")
            tweet_text_by_id = {t[0]: t[1] for t in cursor.fetchall()}

        for tweet in tweets_to_update:
            assert tweet["text"] == tweet_text_by_id[tweet["id"]]


if __name__ == "__main__":
    main()
