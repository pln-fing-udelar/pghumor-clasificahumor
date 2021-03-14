#!/usr/bin/env python
import argparse
import sys

import tweepy

import util


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status: tweepy.Status) -> None:
        if util.status_is_valid(status):
            print(util.status_to_dict(status))

    def on_error(self, status_code: int) -> None:
        print("Error:", status_code, file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", default="es", help="language of the tweets to extract (default: es)")
    args = parser.parse_args()

    api = util.create_tweepy_api()
    stream = tweepy.Stream(auth=api.auth, listener=MyStreamListener())
    stream.sample(languages=[args.language])


if __name__ == "__main__":
    main()
