#!/usr/bin/python3

import tweepy
from consolemenu import *
from consolemenu.items import *
import os
from colorama import Fore, Back, Style
import datetime as dt
import time
from decouple import config

PATTERN_ACCEPTED = {
    "RT",
    "#RT",
    "+RT"
}
LENGTH_PATTERN = len(PATTERN_ACCEPTED)
params = {}


def setup_params() -> None:
    params["consumer_key"] = config('consumer_key')
    params["consumer_secret"] = config('consumer_secret')
    params["access_token_key"] = config('access_token_key')
    params["access_token_secret"] = config('access_token_secret')


class Twitter(tweepy.API):
    def __init__(self, **tokens):
        self.__dict__.update(tokens)
        self.auth = tweepy.OAuthHandler(self.consumer_key,
                                        self.consumer_secret)
        self.auth.set_access_token(self.access_token_key,
                                   self.access_token_secret)
        super().__init__(self.auth,
                         wait_on_rate_limit_notify=True,
                         wait_on_rate_limit=True)

    @staticmethod
    def range_date() -> tuple:
        until = dt.datetime.now()
        since = until - dt.timedelta(days=7)
        return f"{since.year}-{since.month}-{since.day}", \
               f"{until.year}-{until.month}-{until.day}"

    def _input_min_followers(self) -> int:
        try:
            min_follow = int(input("> Minimum followers the user "
                                   "must have [0; +Inf] >> "))
            return min_follow
        except ValueError:
            print("It should be an integer!")
            return self._input_min_followers()

    def _keep_verified(self):
        try:
            keep_verified = input("> Do you want to keep "
                                  "the verified user ? (y/n) >> ")
            return True if keep_verified.lower() == "y" else False
        except ValueError:
            print("It should be a string!")
            return self._keep_verified()

    def friends_cleaner(self) -> None:
        keep_verified = self._keep_verified()
        min_follow = self._input_min_followers()
        friends_count = int(self.me().friends_count)
        sleeper = .8
        self.colorize_string(Fore.BLUE,
                             "> This operation will take at least"
                             f" {friends_count * sleeper}s +"
                             " the rate limit time")
        for friend in tweepy.Cursor(self.friends).items():
            try:
                if keep_verified:
                    if not friend.verified and friend.followers_count < min_follow:
                        self.destroy_friendship(friend.id)
                        self.colorize_string(
                            Fore.LIGHTBLUE_EX,
                            f"> {str(friend.id)}{Style.RESET_ALL}"
                            f"{Fore.LIGHTRED_EX}"
                            " deleted"
                            )
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
    def colorize_string(color: str, string: str) -> None:
        print(color + "> " + string + Style.RESET_ALL)

    def _follow_author(self, user: int) -> None:
        if user.following == False:
            self.create_friendship(user.id)
            self.colorize_string(
                    Fore.GREEN,
                    user.screen_name + Fore.GREEN + " author followed"
                    )

    def _follow_entities(self, user_mentions: list, author_name: str) -> None:
        for e in user_mentions:
            if e.get("screen_name") != author_name:
                self.create_friendship(e.get("id"))
                self.colorize_string(
                    Fore.LIGHTBLUE_EX,
                    e.get("screen_name") + Fore.GREEN + " third entitie followed"
                )

    def _retweet(self, tweet: int) -> None:
        self.retweet(tweet.id)
        self.colorize_string(
            Fore.LIGHTBLUE_EX,
            str(tweet.id) + Fore.GREEN + " retweeted"
        )

    def is_retweeted(self, tweet):
        return self.get_status(tweet.id).retweeted

    def core(self):
        query = input("> Type what you want to be"
                      " searched on twitter (Example : #concours) >> ")
        keep_verified = self._keep_verified()
        min_followers = self._input_min_followers()
        if len(query):
            self.colorize_string(Fore.LIGHTMAGENTA_EX, "Bot starting...")
            while True:
                # __range_date = self.range_date()
                for tweet in tweepy.Cursor(self.search,
                                           q=query,
                                           count=200,
                                           rpp = 100,
                                        #    since=__range_date[0],
                                        #    until=__range_date[1],
                                           tweet_mode='extended').items():
                    user = tweet.user
                    if user.followers_count >= min_followers \
                            and tweet.retweeted is False:
                        text = {t.upper().replace("\n", "") for t in tweet.full_text.split(" ")}
                        try:
                            if keep_verified:
                                if tweet.user.verified and len(PATTERN_ACCEPTED - text) < LENGTH_PATTERN:
                                    tweet_url = f"https://twitter.com/{user.screen_name}/status/{tweet.id}"
                                    self.colorize_string(
                                        Back.BLUE,
                                        "> Tweet " + tweet_url
                                        )
                                    self._follow_author(user)
                                    self._follow_entities(tweet.entities.get("user_mentions"), user.screen_name) 
                                    self._retweet(tweet)
                                    print()
                            else:
                                if len(PATTERN_ACCEPTED - text) < LENGTH_PATTERN:
                                    tweet_url = f"https://twitter.com/{user.screen_name}/status/{tweet.id}"
                                    self.colorize_string(
                                        Back.BLUE,
                                        "Tweet " + tweet_url
                                        )
                                    self._follow_author(user)
                                    self._follow_entities(tweet.entities.get("user_mentions"), user.screen_name)
                                    self._retweet(tweet)
                                    print()
                        except tweepy.TweepError as response:
                            if response.api_code == 327:
                                self.colorize_string(Fore.LIGHTRED_EX,
                                                     "Already retweeted")
                            else:
                                print(response)
            os.system("pause")

    # def test(self):
    #     print(self.get_status(1190644559329611776)._json)
    #     input()

    def run(self, *args, **kwargs):
        try:
            menu = ConsoleMenu("Twitter bot",
                               "Author : https://github.com/takitsu21/")
            menu_item = MenuItem("Menu")
            tweet_by_query = FunctionItem("RT to gain prizes", self.core)
            clean_friends = FunctionItem("Clean friends (choose verified, minimum followers to keep)",
                                         self.friends_cleaner)
            # test = FunctionItem("Debug", self.test)

            # selection_menu = SelectionMenu(os.listdir())
            # submenu_item = SubmenuItem("Submenu item", selection_menu, menu)
            menu.append_item(menu_item)
            # menu.append_item(test)

            menu.append_item(tweet_by_query)
            menu.append_item(clean_friends)
            # menu.append_item(submenu_item)
            menu.show()
        except KeyboardInterrupt:
            menu.show()


if __name__ == "__main__":
    setup_params()
    t = Twitter(**params)
    t.run()
