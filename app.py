#!/usr/bin/python3

import tweepy
from consolemenu import *
from consolemenu.items import *
import os
from colorama import Fore, Back, Style
import datetime as dt
import time
import configparser

PATTERN_ACCEPTED = {
    "RT",
    "#RT",
    "RETWEET",
    "#RETWEET"
}
TO_FOLLOW = {
    "FOLLOW",
    "+FOLLOW"
}
LENGTH_PATTERN = len(PATTERN_ACCEPTED)
LENGTH_TO_FOLLOW = len(TO_FOLLOW)
params = {}


def setup_params() -> None:
    global params
    config = configparser.ConfigParser()
    config.read("setup.ini")
    config = config["TOKENS"]
    params["consumer_key"] = config["consumer_key"]
    params["consumer_secret"] = config["consumer_secret"]
    params["access_token_key"] = config["access_token_key"]
    params["access_token_secret"] = config["access_token_secret"]


class Twitter(tweepy.API):
    def __init__(self, lang: str = "fr", **tokens):
        self.__dict__.update(tokens)
        self.auth = tweepy.OAuthHandler(self.consumer_key,
                                        self.consumer_secret)
        self.auth.set_access_token(self.access_token_key,
                                   self.access_token_secret)
        super().__init__(self.auth,
                         wait_on_rate_limit_notify=True,
                         wait_on_rate_limit=True)
        self.lang = lang

    @staticmethod
    def range_date() -> tuple:
        until = dt.datetime.now()
        since = until - dt.timedelta(days=7)
        return f"{since.year}-{since.month}-{since.day}", \
               f"{until.year}-{until.month}-{until.day}"

    def friends_cleaner(self) -> None:
        keep_verified = input("> Do you want to keep"
                              "your verified friend ? (y/n) ")
        keep_verified = True if keep_verified.lower() == "y" else False
        followers_count = int(self.me().followers_count)
        sleeper = .8
        self.colorize_string(Fore.YELLOW,
                             "This operation will take at least"
                             f"{followers_count * sleeper}s +"
                             " the rate limit time")
        for friend in tweepy.Cursor(self.friends).items():
            try:
                if keep_verified:
                    if not friend.verified:
                        self.destroy_friendship(friend.id)
                        self.colorize_string(
                            Fore.LIGHTBLUE_EX,
                            f"{str(friend.id)}{Style.RESET_ALL}"
                            f"{Fore.LIGHTRED_EX}"
                            " deleted")
                        time.sleep(sleeper)
                else:
                    self.destroy_friendship(friend.id)
                    self.colorize_string(
                            Fore.LIGHTBLUE_EX,
                            f"{str(friend.id)}{Style.RESET_ALL}"
                            f"{Fore.LIGHTRED_EX}"
                            " deleted"
                        )
                    time.sleep(sleeper)
            except KeyboardInterrupt:
                exit()

    @staticmethod
    def colorize_string(color, string: str) -> None:
        print(color + string + Style.RESET_ALL)

    def _follow_author(self, _id: int, screen_name: str) -> None:
        self.create_friendship(_id)
        self.colorize_string(
            Fore.GREEN,
            screen_name + Fore.GREEN + " author followed"
            )

    def _follow_entities(self, user_mentions: list) -> None:
        for e in user_mentions:
            self.create_friendship(e.id)
            self.colorize_string(
                Fore.LIGHTBLUE_EX,
                e.screen_name + Fore.GREEN + " third entitie followed"
            )

    def _retweet(self, _id: int) -> None:
        self.retweet(_id)
        self.colorize_string(
            Fore.LIGHTBLUE_EX,
            str(_id) + Fore.GREEN + " retweeted"
        )

    def is_retweeted(self, tweet_id):
        return self.get_status(tweet_id).retweeted

    def core(self):
        query = input("> Type what you want to be"
                      " searched on twitter (Example : #concours) >> ")
        if len(query):
            while True:
                __range_date = self.range_date()
                for tweet in tweepy.Cursor(self.search,
                                           q=query,
                                           lang=self.lang,
                                           since=__range_date[0],
                                           until=__range_date[1],
                                           tweet_mode='extended').items():
                    user = tweet.user
                    if user.followers_count >= 8000 \
                            and not self.is_retweeted(tweet.id):
                        text = {t.upper() for t in tweet.full_text.split(" ")}
                        if len(PATTERN_ACCEPTED - text) < LENGTH_PATTERN:
                            self.colorize_string(
                                Back.LIGHTBLUE_EX,
                                "Tweet " + str(tweet.id)
                            )
                            self._follow_author(user.id, user.screen_name)
                            if len(TO_FOLLOW - text) < LENGTH_TO_FOLLOW:
                                self._follow_entities(
                                    tweet.entities.get("user_mentions")
                                )
                            self._retweet(tweet.id)
                            print()
            os.system("pause")

    def test(self):
        query = input("> Type what you want to be"
                      " searched on twitter (Example : #concours) >> ")
        __range_date = self.range_date()

        for tweet in tweepy.Cursor(self.search,
                                   q=query,
                                   lang=self.lang,
                                   since=__range_date[0],
                                   until=__range_date[1],
                                   tweet_mode='extended').items(1):
            print(tweet._json)
        os.system("pause")

    def run(self, *args, **kwargs):
        try:
            menu = ConsoleMenu("Twitter bot",
                               "Author : https://github.com/takitsu21/")
            menu_item = MenuItem("Menu Item")
            tweet_by_query = FunctionItem("Get tweet by query", self.core)
            clean_friends = FunctionItem("Clean all friends",
                                         self.friends_cleaner)
            test = FunctionItem("Debug", self.test)

            selection_menu = SelectionMenu(os.listdir())
            submenu_item = SubmenuItem("Submenu item", selection_menu, menu)
            menu.append_item(menu_item)
            menu.append_item(test)

            menu.append_item(tweet_by_query)
            menu.append_item(clean_friends)
            menu.append_item(submenu_item)
            menu.show()
        except KeyboardInterrupt:
            menu.show()


if __name__ == "__main__":
    setup_params()
    t = Twitter(**params)
    t.run()
