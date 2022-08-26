import tweepy
import os
import time
from os.path import expanduser
from dotenv import load_dotenv
from vividbot.telebot import telegram_bot_sendtext
from tabulate import tabulate
# import pandas as pd
import json
from collections import OrderedDict
import re
import ast
import urllib.request

env_path = expanduser("~/.env_VH") # use the env for testing, 2 is the real loggin
load_dotenv(dotenv_path=env_path, override=True)


client = tweepy.Client(consumer_key=os.getenv("CONSUMER_KEY"),
                       consumer_secret= os.getenv("CONSUMER_SECRET"),
                       access_token=os.getenv("ACCESS_TOKEN"),
                       access_token_secret=os.getenv("ACCESS_SECRET"))

substance_url = "https://raw.githubusercontent.com/ViewsOnDrugs/vivid_substanzen/master/data/substances.json"

with urllib.request.urlopen(substance_url) as fp:
    substance_dic = json.load(fp)

substance_dic = {k.lower(): v for k, v in substance_dic.items()}

substance_list = substance_dic.keys()

post_infos_de = ["Beschreibung", "Konsumform", "Kombinationen",
                 "dose_dict", "wirkdauer_dict", "comment", "VIVID Safer-Use Tipps"]


def shorten_wirkungsein(in_dict):
    for x in in_dict:
        for i in in_dict[x]:
            if "_dict" in i:
                reps = ast.literal_eval(str(in_dict[x][i]).replace("Wirkungseintritt", "W.eintritt"))
                in_dict[x][i] = reps
    return in_dict


substance_dic = shorten_wirkungsein(substance_dic)


def replace_emojis_unicode(replace_string):
    replace_emojis = {":pig_nose:": "\U0001f43d", ":lips:": "\U0001f444",
                      ":arrow_up_small:": "\U000023EB",
                      ":warning:": "\U00002757", ":syringe:": "\U0001f489", ":fog:": "\U0001f32b",
                      ":tongue:": "\U0001f445",
                      ":arrow_down_small:": "\U000023EC"}

    for word, replacement in replace_emojis.items():
        replace_string = re.sub(word, replacement, replace_string)
    return (replace_string)


tittles_list = ["Beschreibung", "Konsumform", "Kombinationen"]


def smart_truncate(content, length=250, suffix='...'):
    """
    truncate to string to not exceed the 280 characters of a tweet
    """
    total_length = len(content)
    half_length = round(total_length / 2)

    if total_length >= length:
        first_part = ' '.join(content[:half_length].split(' ')[0:-1]) + suffix
        second_part = suffix + ' '.join(content[len(first_part) - 2:].split(' ')[0:])
        if len(second_part) >= 2:
            return first_part, second_part
        else:
            first_part, None

def update_thread(text: str, tweet: str) -> str:
    """
    Add a tweet to a initiated thread
    Args:
        text: text to add to tweet as thread
        tweet: tweepy status to add reply to
    Returns: post a reply to a tweet
    """
    return client.create_tweet(text=text, in_reply_to_tweet_id=tweet.data["id"])


def post_thread(dict_info_subst: dict, tweet_id: int) -> int:
    """
    Initiate and post a thread of tweets
    Args:
        dict_info_subst: dictionary object with processed publication item
        tweet_id: id of tweet to reply to
    Returns: tweet id of the first tweet of thread
    """

    telegram_bot_sendtext(f"Posting thread:, twitter.com/i/status/{tweet_id}")

    limit = dict_info_subst["tw_length"]
    count = 0

    del dict_info_subst["tw_length"]

    original_tweet = client.create_tweet(text=dict_info_subst[list(dict_info_subst)[count]],
                                         in_reply_to_tweet_id=tweet_id, )

    reps_dict = {}
    "tw_length"
    while count < limit:

        count += 1
        time.sleep(2)

        text_list = [dict_info_subst[c] for c in dict_info_subst]

        if count == 1:

            reps_dict[f"reply{str(count)}"] = update_thread(text_list[count],
                                                            original_tweet)
        elif count > 1 and count <= limit - 1:
            reps_dict[f"reply{str(count)}"] = update_thread(text_list[count],
                                                            reps_dict[f"reply{str(count - 1)}"]
                                                            )

        else:
            end_mess = """Weitere Informationen zum Safer-Use und Substanzen findest du unter: https://vivid-hamburg.de/substanzen 
folge auch @ViewsOnDrugsBot"""
            update_thread(end_mess, reps_dict[f"reply{str(count - 1)}"])

            break

    return original_tweet.data["id"]


format_substs = " -" + "\n -".join(substance_list)
# to_post_dict = make_substance_dict()

to_post_dict = json.load(open('substanzen.json'), object_pairs_hook=OrderedDict)




class IDPrinter(tweepy.StreamingClient):

    def on_tweet(self, status):

        print(status)
        if status.referenced_tweets:  # Check if Retweet
            print(f" check if retweet:, {status['referenced_tweets']}")
        else:
            try:
                ## catch nesting
                answer_id = status.id
                ## ignore replies that by default contain mention
                status_text = status.text.lower()

            except AttributeError:

                answer_id = status.id

            update_status = f"""Für Safer-Use Infos tweete an @VIVIDHamburg mit einem dieser Substanzen: 
{format_substs} 

oder tweete 
@VIVIDHamburg -info um diese Info zu erhalten
"""

            # Warning: don't reply infinite times to yourself!!
            #             self_ids=[1319577341056733184, 1520821277174517760]
            if '-' in status_text:

                info_subs = status_text.split("-")[1]

                if "2-cb" in status_text:
                    info_subs = "2-cb"

                if info_subs in substance_list:
                    post_thread(to_post_dict[info_subs], tweet_id=answer_id)


                elif "info" in info_subs:

                    client.create_tweet(text=update_status,
                                        in_reply_to_tweet_id=answer_id)
                    print(answer_id, "info")
                else:  # add exception when privileges are elevated TODO
                    #                     if status.user["id"] != 1520821277174517760:
                    #                         subs_not_found=f"-{info_subs} ist keine gültige Substanz antworte mit -start für mehr Infos"
                    #                         client.create_tweet(text=subs_not_found,
                    #                                             in_reply_to_tweet_id=answer_id)
                    print(answer_id, info_subs, substance_list)
                    pass

    def on_error(self, status):
        # telegram_bot_sendtext(f"ERROR with: {status}")
        print(f"ERROR with: {status}")


def listen_stream_and_rt():
    printer = IDPrinter(os.getenv("BEARER_TOKEN"))
    try:

        printer.add_rules(tweepy.StreamRule("VIVIDHamburg"))
        printer.filter()
    except Exception as ex:
        # telegram_bot_sendtext(f"ERROR {ex} with: {status}")
        print(f"ERROR {ex}")

        pass

# listen to every mention of the bot but only interact with those having
# - and one of the substances on ´substance_list´ or -start


if __name__ == "__main__":

    listen_stream_and_rt()
