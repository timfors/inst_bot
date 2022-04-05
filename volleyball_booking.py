import requests
import time
from time import sleep
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.chat import Chat
from datetime import datetime, timezone, timedelta
import json
from bs4 import BeautifulSoup

headers = {
    'authorization': 'Bearer 3e074e13bad6bb467edb5b21c62ae2aeb47fbbab'
}
dataThursday = {
    "clubId": 1083,
    "scheduleId": 151262024022022
}
dataTuesday = {
    "clubId": 1083,
    "scheduleId": 151171801032022
}

url = "https://mobifitness.ru/api/v6/account/reserve.json"
update_url = "https://mobifitness.ru/api/v6/club/1083/schedule.json"



def get_day():
    return datetime.today().isoweekday()

def check_time(h, m):
    t = datetime.now(timezone(timedelta(hours=3))).time()
    if t.hour == h and t.minute == m:
        return True
    return False


data_ids = []


def update_volley(activity_id):
    global data_ids
    r = requests.get(update_url, headers=headers).text
    data = json.loads(r)
    data_ids = [x['id'] for x in data["schedule"] if x['activity']['id'] == activity_id]


def try_reserve(id: int):
    response = requests.post(url=url, headers=headers, data={"clubId": 1083, "scheduleId": data_ids[id]})
    return response.status_code

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_updater = Updater("1284907032:AAH1pXYVcn8zp6oqtdaw_YWuQtDEiHf36d4")
telegram_updater.start_polling()
time.timezone = 3
lastTime = time.time()
t = datetime.now(timezone(timedelta(hours=3))).time()
update_volley(46588)
while True:
    if get_day() == 1 and check_time(0, 0):
        update_volley(46588)
    if get_day() == 2:
        response = try_reserve(0)
        if response == 200:
            chat = Chat(id=322726399, bot=telegram_updater.bot, type="private")
            chat.send_message("Записался на волейбол")
    elif get_day() == 4:
        response = try_reserve(1)
        if response == 200:
            chat = Chat(id=322726399, bot=telegram_updater.bot, type="private")
            chat.send_message("Записался на волейбол")
telegram_updater.idle()


