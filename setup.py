#!/usr/bin/env python3
from setuptools import setup

setup(
    name="vivid_twitter_bot",
    version="0.1",
    description="Bot for substanzen ",
    url="https://github.com/ViewsOnDrugs/vivid_bot",
    license="GNU Affero General Public License v3.0",
    packages=["vividbot"],
    keywords=[
        "sci-com",
        "drug policy",
        "research",
        "science",
        "drugs",
    ],
    entry_points={
        "console_scripts": [
            "vividstream=vividbot.main:listen_stream_and_rt",
        ]
    },
    install_requires=[
        "beautifulsoup4==4.9.3",
        "feedparser==6.0.2",
        "oauthlib==3.2.0",
        "python-dotenv==0.15.0",
        "requests==2.27.0",
        "requests-oauthlib==1.3.0",
        "schedule==0.6.0",
        "telebot==0.0.4",
        "Telethon==1.18.2",
        "tweepy==4.10.1",
        "urllib3==1.26.2",
    ],
    zip_safe=False,
)