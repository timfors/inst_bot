import json
import random
from time import sleep
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.chat import Chat
from instagrapi import Client
from inst_account import InstAccount


def load_json(path):
    data = {}
    accounts = []
    try:
        with open(path, 'r') as progress:
            data = json.load(progress)
            for username, value in data.items():
                accounts.append(InstAccount(username, [int(value) for key, value in value["telegrams"].items()],
                                            list(value["followers"].values())))
    except Exception:
        return accounts
    return accounts


def save_json(data, path):
    formated = {}
    for account in accounts_instagram:
        formated[account.username] = account.to_json()
    with open(path, 'w') as progress:
        json.dump(formated, progress)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_updater = Updater("1284907032:AAH1pXYVcn8zp6oqtdaw_YWuQtDEiHf36d4")
telegram_dispatcher = telegram_updater.dispatcher

accounts_instagram = load_json("progress.json")
instagram = Client()
instagram.login(username="timfors003", password="weas2222")


def get_followers(username):
    return [user.username for user in instagram.user_followers_v1(instagram.user_id_from_username(username))]


def add_username(username, telegram_id, accounts = []):
    matches = [account for account in accounts if account.username == username]
    if len(matches) > 0:
        if telegram_id in matches[0].telegrams:
            return f"Дак мы же уже следим за @{username}. Ну ты даешь, подруга..."
        matches[0].telegrams.append(telegram_id)
        save_json(accounts, "progress.json")
    else:
        try:
            followers = get_followers(username)
            accounts.append(InstAccount(username, [telegram_id], followers))
            save_json(accounts, "progress.json")
        except Exception:
            return f"Без понятия, что не так с {username}.Попробуй еще раз"
    return f"Оки-доки, наблюдаю за подписками|отписками у @{username}"


def remove_username(username, telegram_id, accounts = []):
    matches = [account for account in accounts if account.username == username and telegram_id in account.telegrams]
    if len(matches) > 0:
        matches[0].telegrams.remove(telegram_id)
        if len(matches[0].telegrams) == 0:
            accounts.remove(matches[0])
        save_json(accounts, "progress.json")
        return f"Все! Отныне мне похуй на @{username}"
    else:
        return f"Я хз, ошибка у тебя или нет, но за @{username} и так слежки не было"


def set(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    usernames = update.message.text.split(' ')
    usernames.pop(0)
    for username in usernames:
        update.message.reply_text(add_username(username, chat_id, accounts_instagram))


def unset(update: Update, contex: CallbackContext):
    chat_id = update.message.chat_id
    usernames = update.message.text.split(' ')
    usernames.pop(0)
    for username in usernames:
        update.message.reply_text(remove_username(username, chat_id, accounts_instagram))


def get_followers_text(account: InstAccount, followers):
    followers_dict = ['Заи Дня для ', 'Встречайте новобранцев в рядах ',
                      'Работяги, достойные внимания для ', "Подписались на ",
                      "Пополнение в болоте "]
    followers_usernames = "".join(['\n@' + str(username) for username in followers])
    return followers_dict[random.Random().randint(a=0, b=len(followers_dict) - 1)] + f"@{account.username}:\n" + followers_usernames + "\n\n"


def get_unfollowers_text(account: InstAccount, unfollowers):
    unfollowers_dict = ['Гандилы для ', 'В них может плеваться  ',
                        'Пид#расы у ', "Ушли и похуй ",
                        "Какие же чмины были у заи "]
    followers_usernames = "".join(['\n@' + str(username) for username in unfollowers])
    return unfollowers_dict[random.Random().randint(a=0, b=len(unfollowers_dict) - 1)] + f"@{account.username}:\n" + followers_usernames + "\n\n"


def check_account(account: InstAccount):
    followers = get_followers(account.username)
    text = ""
    new_followers, unfollowers = account.check_followers(followers)
    text += get_followers_text(account, new_followers) if len(new_followers) > 0 else ""
    text += get_unfollowers_text(account, unfollowers) if len(unfollowers) > 0 else ""
    if text != "":
        account.followers = followers
        save_json(accounts_instagram, "progress.json")
        for chat_id in account.telegrams:
            chat = Chat(id=chat_id, bot=telegram_updater.bot, type="private")
            chat.send_message(text)


def check_accounts():
    delay_time = len(accounts_instagram) ** 0.5
    for account in accounts_instagram:
        check_account(account)
        sleep(delay_time)


def monitorings(update: Update, contex: CallbackContext):
    telegram_id = update.message.chat_id
    target_users = [account.username for account in accounts_instagram if telegram_id in account.telegrams]
    text = "Специально для тебя! И только для тебя! Слежу за:\n"
    text += "\n".join(map(str, target_users))
    text += "\nМожешь не благодарить."
    update.message.reply_text(text)


telegram_dispatcher.add_handler(CommandHandler("set", set))
telegram_dispatcher.add_handler(CommandHandler("unset", unset))
telegram_dispatcher.add_handler(CommandHandler("monitorings", monitorings))
telegram_updater.start_polling()
while True:
    sleep(300)
    check_accounts()
telegram_updater.idle()
