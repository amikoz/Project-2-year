from __future__ import unicode_literals
import flask
import telebot
import conf
import sys                                                                                                                
import os
sys.path.append('/usr/local/lib/python3.5/dist-packages')

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)  # бесплатный аккаунт pythonanywhere запрещает работу с несколькими тредами

# удаляем предыдущие вебхуки, если они были
bot.remove_webhook()

# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

import tweepy
from credentials import *
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
from matplotlib.font_manager import FontProperties

prop = FontProperties()
prop.set_file('/home/kozenasheva/STIXv2.0.0/Fonts/OTF/STIX2Text-Regular.otf')

def extract_hashtags(text):
    return [part[1:] for part in text.split() if part.startswith('#')]

@bot.message_handler(commands=['help'])
def send_welcome(message):
        bot.send_message(message.chat.id, "Это бот, который строит график частотности употребления 10 самых популярных хэштегов пользователя. Просто введите любой username из твиттера.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
        bot.send_message(message.chat.id, "Здравствуйте! Это бот, который строит график частотности употребления 10 самых популярных хэштегов пользователя. Просто введите любой username из твиттера.")

@bot.message_handler(func=lambda m: True)  # этот обработчик реагирует все прочие сообщения
def send_len(message):
    try:
        user = api.get_user(screen_name = message.text)
    except tweepy.error.TweepError:
        bot.send_message(message.chat.id, "К сожалению, пользователь не найден")
        return
    hashtags_dict = defaultdict(int)
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=message.text).items():
        for hashtag in extract_hashtags(tweet.text):
            print(type(hashtag))
            print(hashtag.encode('utf-8'))
            hashtags_dict[hashtag] += 1

    if len(hashtags_dict) == 0:
        bot.send_message(message.chat.id, "Этот пользователь не использовал хэштеги")
        return
    to_draw = dict(sorted(hashtags_dict.items(),key=lambda x: x[1], reverse=True)[:10])
    plt.bar(np.arange(len(to_draw.keys())), to_draw.values(), width=1.0, color='g', align='center')
    plt.ylabel("Hashtags")
    plt.ylabel("Hashtag frequency")
    plt.xticks(np.arange(len(to_draw.keys())), to_draw.keys(), rotation='vertical', fontproperties=prop)
    plt.tight_layout()
    plt.savefig('figure.png')
    image = open('figure.png', 'rb')
    bot.send_photo(message.chat.id, image)
    os.remove('figure.png')

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

