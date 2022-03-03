import requests
import time
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
    return datetime.datetime.today().isoweekday()

def check_time(h, m):
    t = datetime.now(timezone(timedelta(hours=8))).time()
    if t.hour == h and t.minute == m:
        return True
    return False

def try_reserve(activity_id):
    r = requests.get(update_url, headers=headers).text
    data = json.loads(r)
    data_ids = [x['id'] for x in data["schedule"] if x['activity']['id'] == activity_id]
    requests.post(url=url, headers=headers, data={"clubId": 1083, "scheduleId": data_ids[0]})
    requests.post(url=url, headers=headers, data={"clubId": 1083, "scheduleId": data_ids[1]})
    return None