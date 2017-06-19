import tweepy
from credentials import *
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


import sys
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

def extract_hashtags(text):
    return [part[1:] for part in text.split() if part.startswith('#')]

hashtags_dict = defaultdict(int)
for tweet in tweepy.Cursor(api.user_timeline, screen_name='kozenasheva').items():
    for hashtag in extract_hashtags(tweet.text):
        hashtags_dict[hashtag] += 1

plt.bar(np.arange(len(hashtags_dict.keys())), hashtags_dict.values(), width=1.0, color='g')
plt.xticks(np.arange(len(hashtags_dict.keys())), hashtags_dict.keys())
