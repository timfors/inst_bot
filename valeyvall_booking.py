import requests
import time
import datetime
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

if (time.timezone != -10800):
    time.timezone = -10800


def get_day():
    return datetime.datetime.today().isoweekday()


def try_reserve(h, m):
    r = requests.get(update_url, headers=headers).text
    data = json.loads(r)
    data_ids = [x['id'] for x in data["schedule"] if x['activity']['id'] == 46588]
    t = time.localtime(time.time())
    if t.tm_hour == h and t.tm_min == m:
        requests.post(url=url, headers=headers, data={"clubId": 1083, "scheduleId": data_ids[0]})
        requests.post(url=url, headers=headers, data={"clubId": 1083, "scheduleId": data_ids[1]})
    return None
