import requests
import time
import datetime

headers = {
    'authorization': 'Bearer 3e074e13bad6bb467edb5b21c62ae2aeb47fbbab'
}
dataThursday = {
    "clubId": 1083,
    "scheduleId": 151262024022022
}

dataTuesday = {
    "clubId": 1083,
    "scheduleId": 151171822022022
}
url = "https://mobifitness.ru/api/v6/account/reserve.json"


def get_day():
    return datetime.datetime.today().isoweekday()


def try_tuesday():
    if time.timezone != -10800:
        time.timezone = -10800
    t = time.localtime(time.time())
    if t.tm_hour == 17 and t.tm_min == 0:
        return requests.post(url=url, headers=headers, data= dataTuesday)
    return None


def try_thursday():
    if time.timezone != -10800:
        time.timezone = -10800
    t = time.localtime(time.time())
    if t.tm_hour == 18 and t.tm_min == 0:
        return requests.post(url=url, headers=headers, data=dataTuesday)
    return None
