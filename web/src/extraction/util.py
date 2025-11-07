import fileinput
import json
import os
import re
from typing import Any, Iterable, MutableMapping, Optional, Sequence, TypeVar

import MySQLdb.connections
import tweepy

TYPE_TWEET = MutableMapping[str, Any]

RE_LINK = re.compile(r"https?://")


def read_tweets_from_input(path: Optional[str] = None, json_format: bool = True) -> Iterable[TYPE_TWEET]:
    return read_tweets(fileinput.input(path), json_format)


def read_tweets(file: Iterable[str], json_format: bool = True) -> Iterable[TYPE_TWEET]:
    return [deserialize_tweet(line) if json_format else eval(line) for line in file]


def status_is_retweet(status: tweepy.Status) -> bool:
    return hasattr(status, "retweeted_status")


def status_is_quote(status: tweepy.Status) -> bool:
    return status.is_quote_status  # noqa


def status_is_reply(status: tweepy.Status) -> bool:
    return status.in_reply_to_status_id  # noqa


def status_contains_a_link(status: tweepy.Status) -> bool:
    return bool(RE_LINK.search(status.text))  # noqa


def status_is_valid(status: tweepy.Status) -> bool:
    return not status_is_retweet(status) \
           and not status_is_quote(status) \
           and not status_is_reply(status) \
           and not status_contains_a_link(status)


def status_to_dict(status: tweepy.Status) -> TYPE_TWEET:
    return {
        "id": status.id,  # noqa
        "text": status.text,  # noqa
        "user_id": status.author.id,  # noqa
    }


def serialize_tweet(tweet: TYPE_TWEET) -> str:
    return json.dumps(tweet)


def deserialize_tweet(text: str) -> TYPE_TWEET:
    return json.loads(text)


def create_tweepy_auth(app_only_auth: bool = False) -> tweepy.auth.AuthHandler:
    consumer_token = os.environ["CONSUMER_TOKEN"]
    consumer_secret = os.environ["CONSUMER_SECRET"]

    if app_only_auth:
        return tweepy.AppAuthHandler(consumer_token, consumer_secret)
    else:
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth


def create_tweepy_api(app_only_auth: bool = False) -> tweepy.API:
    return tweepy.API(auth_handler=create_tweepy_auth(app_only_auth))


T = TypeVar("T")


def chunks(seq: Sequence[T], n: int) -> Sequence[Sequence[T]]:
    """Yield successive n-sized chunks."""
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def create_connection() -> MySQLdb.connections.Connection:
    return MySQLdb.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USER"], password=os.environ["DB_PASS"],
                           database=os.environ["DB_NAME"], charset="utf8mb4")
