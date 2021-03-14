#!/usr/bin/env python
"""This script is used to fix a file we want to use as input of "persist.py", when it has a particular encoding problem.
The problem seems to be related with a difference between how different Python versions handle string literals.
First, note that the input file is not a real json, but a list of Python dicts printed (i.e., `print(dict)` vs
`print(json.dumps(dict))`). So, there are string literals. The file may be in UTF-8, but the thing is that the string
literals may contain Unicode-escaped symbols (e.g., `\\xNN`, `\\uNN` or `\\UNNNN`), which represent bytes in different
encodings. In the default compiled version of CPython 3.6 in Linux, it represents them internally in UTF-8, but
in Python 2.7 apparently it does so UTF-16, or at least that's my understanding (see
https://docs.python.org/2/howto/unicode.html#the-unicode-type). So Unicode-escaped symbols change.
I don't find an easy way to fix it, more than re-downloading the tweets, which is fairly fast."""

import logging
import time

from tqdm import tqdm

import util

USER_AUTH_STATUSES_LOOKUP_RATE_LIMIT_PER_WINDOW = 900
SECS_IN_A_MINUTE = 60
DELAY_PER_USER_AUTH_STATUSES_LOOKUP_REQUEST = 15 * SECS_IN_A_MINUTE / USER_AUTH_STATUSES_LOOKUP_RATE_LIMIT_PER_WINDOW
MAX_STATUSES_COUNT_PER_STATUSES_LOOKUP = 100


def main():
    tweets = util.read_tweets_from_input()

    api = util.create_tweepy_api()

    with tqdm(total=len(tweets), desc="Re-fetching tweets") as progress_bar:
        # TODO: only re-download the ones with encoding issues. Don't touch the rest.
        for tweet_group in util.chunks(tweets, MAX_STATUSES_COUNT_PER_STATUSES_LOOKUP):
            # Consider that the key name may vary between 'tweet_id' or 'id' depending on the input file.
            queried_statuses = api.statuses_lookup((tweet['tweet_id'] for tweet in tweet_group), map_=False)
            queried_statuses_by_id = {queried_status.id: queried_status for queried_status in queried_statuses}
            for original_tweet in tweet_group:
                id_ = original_tweet['tweet_id']
                queried_status = queried_statuses_by_id.get(id_)
                if queried_status:
                    original_tweet['text'] = queried_status.text
                    print(original_tweet)
                else:
                    logging.warning(f"Failed to fetch the following tweet ID: {id_}.\n"
                                    "Checking its text for encoding problems…")
                    try:
                        original_tweet['text'].encode('utf8')
                        print(original_tweet)
                        logging.warning("No errors. The tweet was written in the output but its text was not replaced.")
                    except UnicodeEncodeError as e:
                        logging.warning(f"Error: {e}Tweet not written in the output.")
            time.sleep(DELAY_PER_USER_AUTH_STATUSES_LOOKUP_REQUEST)
            progress_bar.update(len(tweet_group))


if __name__ == '__main__':
    main()
