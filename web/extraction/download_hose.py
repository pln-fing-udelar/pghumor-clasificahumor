#!/usr/bin/env python
import argparse
import sys

import tweepy

import util
from argparse_with_defaults import ArgumentParserWithDefaults


class StreamListener(tweepy.StreamListener):
    def __init__(self, json_format: bool = True) -> None:
        super().__init__()
        self.json_format = json_format

    def on_status(self, status: tweepy.Status) -> None:
        if util.status_is_valid(status):
            tweet = util.status_to_dict(status)
            print(util.serialize_tweet(tweet) if self.json_format else tweet)

    def on_error(self, status_code: int) -> None:
        print("Error:", status_code, file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = ArgumentParserWithDefaults()
    parser.add_argument("--language", default="es", help="language of the tweets to extract")
    parser.add_argument("--no-json-format", dest="json_format", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stream = tweepy.Stream(auth=util.create_tweepy_auth(), listener=StreamListener(args.json_format))
    stream.sample(languages=[args.language])


if __name__ == "__main__":
    main()
