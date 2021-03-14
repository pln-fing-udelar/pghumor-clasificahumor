#!/usr/bin/env python
import argparse
import time
from typing import Mapping

from tqdm.auto import tqdm

import util
from argparse_with_defaults import ArgumentParserWithDefaults

APP_AUTH_USER_TIMELINE_RATE_LIMIT_PER_WINDOW = 1500
SECS_IN_A_MINUTE = 60
DELAY_PER_APP_AUTH_USER_TIMELINE_REQUEST = 15 * SECS_IN_A_MINUTE / APP_AUTH_USER_TIMELINE_RATE_LIMIT_PER_WINDOW
MAX_STATUSES_COUNT_PER_APP_AUTH_USER_TIMELINE_REQUEST = 200
MAX_STATUSES_COUNT_PER_USER_TIMELINE = 3200

USER_AUTH_USERS_LOOKUP_RATE_LIMIT_PER_WINDOW = 900
DELAY_PER_USER_AUTH_USERS_LOOKUP_REQUEST = 15 * SECS_IN_A_MINUTE / USER_AUTH_USERS_LOOKUP_RATE_LIMIT_PER_WINDOW
MAX_STATUSES_COUNT_PER_USER_AUTH_USERS_LOOKUP_REQUEST = 100

SCREEN_NAMES = [
    "ArgentinaChiste",
    "asaoyvino",
    "BuenasPhrases",
    "BuenosChistes21",
    "CarolAlvo",
    "CausandoRisas",
    "ChisteLoco",
    "CHISTEPIN",
    "ChistesAlDia",
    "ChistesGen",
    "ChisteSorpresa",
    "ChisteUniversal",
    "Chistorreo_",
    "ColombiaChiste",
    "DayalaEC",
    "Ducfius",
    "ElAbueloDemente",
    "ElChisteDelDia",
    "elFerDias",
    "eljueves",
    "EresChiste",
    "EscritosdeHumor",
    "Esepinchewey",
    "GonCuriel",
    "GretchenZanders",
    # "hiletrado",  # Suspended account
    "hum0rdenoche",
    "Hum0rROJO",
    "Humor_Medicos",
    "HumorParaguayo",
    "humortico",
    "HumoryDiversion",
    "iauraB",
    "ImagineSuCara",
    "JajaChistes",
    "L_chiste",
    "Llourinho",
    "lnedito",
    "LosChistes",
    "NiLaMenorIdea_",
    "odiomistweets",
    "Oritavoy",
    "perroblanko666",
    "PitufoFilosofon",
    "SarcasmoChapin",
    "SomosSarcasmo",
    "todochistes",
    "Un_huevo_",
    # "WillyWonkaDice",  # Suspended account
    "ZonaDeRisas",
]


def max_obtainable_status_count_per_user() -> Mapping[str, int]:
    result = {}

    user_api = util.create_tweepy_api(app_only_auth=True)
    for screen_names in util.chunks(SCREEN_NAMES, MAX_STATUSES_COUNT_PER_USER_AUTH_USERS_LOOKUP_REQUEST):
        users = user_api.lookup_users(screen_names=screen_names, include_entities=False)

        result.update((user.screen_name, min(user.statuses_count, MAX_STATUSES_COUNT_PER_USER_TIMELINE))
                      for user in users)

        time.sleep(DELAY_PER_USER_AUTH_USERS_LOOKUP_REQUEST)

    return result


def parse_args() -> argparse.Namespace:
    parser = ArgumentParserWithDefaults()
    parser.add_argument("--no-json-format", dest="json_format", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    status_count_per_user = max_obtainable_status_count_per_user()

    assert all(screen_name in status_count_per_user for screen_name in SCREEN_NAMES), \
        f"The following account names do not match when extracted:" \
        f" {[screen_name for screen_name in SCREEN_NAMES if screen_name not in status_count_per_user]}"

    status_count = sum(count for count in status_count_per_user.values())

    app_api = util.create_tweepy_api(app_only_auth=True)

    with tqdm(total=status_count) as progress_bar:
        max_id = None
        count = 0
        for screen_name in SCREEN_NAMES:
            statuses = ["placeholder"]
            while statuses:
                statuses = app_api.user_timeline(screen_name=screen_name, max_id=max_id, trim_user=True,
                                                 exclude_replies=True, include_rts=False,
                                                 count=MAX_STATUSES_COUNT_PER_APP_AUTH_USER_TIMELINE_REQUEST)
                for status in statuses:
                    if util.status_is_valid(status):
                        tweet = util.status_to_dict(status)
                        print(util.serialize_tweet(tweet) if args.json_format else tweet)

                max_id = statuses.max_id

                time.sleep(DELAY_PER_APP_AUTH_USER_TIMELINE_REQUEST)

                count += len(statuses)
                progress_bar.update(len(statuses))

            if count < status_count_per_user[screen_name]:
                # The param `count` in the request is a max because the exclusion of replies and retweets is done
                # after obtaining the statuses and because the last "page" may have less tweets. So we make up for
                # the missing count after having finished with a user.
                progress_bar.update(status_count_per_user[screen_name] - count)


if __name__ == "__main__":
    main()
