import json
import random
import time
from time import sleep
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.chat import Chat
from instagrapi import Client
from inst_account import InstAccount
from database_work import *
from valeyvall_booking import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

telegram_updater = Updater("1284907032:AAH1pXYVcn8zp6oqtdaw_YWuQtDEiHf36d4")
telegram_dispatcher = telegram_updater.dispatcher

accounts_instagram = load_accounts()
instagram = Client()
instagram.login(username="daunitze", password="ioJfg46*SnmL")


def get_followers(username):
    return [user.username for user in instagram.user_followers_v1(instagram.user_id_from_username(username))]


def add_username(username, telegram_id, t_username, accounts = []):
    matches = [account for account in accounts if account.username == username]
    if len(matches) > 0:
        if telegram_id in matches[0].telegrams:
            return f"Дак мы же уже следим за @{username}. Ну ты даешь, подруга..."
        matches[0].telegrams.append(telegram_id)
        matches[0].telegram_username.append(t_username)
        save_account(matches[0])
    else:
        try:
            user_info = instagram.user_info(instagram.user_id_from_username(username))
            if user_info.is_private:
                return f"Сорямба @{username} приватный.С такими дел не имею."
            followers = get_followers(username)
            new_account = InstAccount(username, [telegram_id], [t_username], followers)
            save_account(new_account)
            accounts.append(new_account)
        except Exception as e:
            print(e)
            return f"Без понятия, что не так с @{username}.Попробуй еще раз"
    return f"Оки-доки, наблюдаю за подписками|отписками у @{username}"


def remove_username(username, telegram_id, t_username, accounts = []):
    matches = [account for account in accounts if account.username == username and telegram_id in account.telegrams]
    if len(matches) > 0:
        matches[0].telegrams.remove(telegram_id)
        matches[0].telegram_username.remove(t_username)
        if len(matches[0].telegrams) == 0:
            remove_account(matches[0])
            accounts.remove(matches[0])
        else:
            save_account(matches[0])
        return f"Все! Отныне мне похуй на @{username}"
    else:
        return f"Я хз, ошибка у тебя или нет, но за @{username} и так слежки не было"


def set(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    t_username = update.message.chat.username
    usernames = update.message.text.split(' ')
    usernames.pop(0)
    for username in usernames:
        update.message.reply_text(add_username(username.replace('@', ''), chat_id, t_username, accounts_instagram))


def unset(update: Update, contex: CallbackContext):
    chat_id = update.message.chat_id
    t_username = update.message.chat.username
    usernames = update.message.text.split(' ')
    usernames.pop(0)
    for username in usernames:
        update.message.reply_text(remove_username(username.replace('@', ''), chat_id, t_username, accounts_instagram))


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
        save_account(account)
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


def all_monitorings(update: Update, contex: CallbackContext):
    printed = []
    if update.message.chat_id != 322726399:
        return
    for account in accounts_instagram:
        for t_user in account.telegram_username:
            if t_user not in printed:
                monitors = [acc.username for acc in accounts_instagram if t_user in acc.telegram_username]
                text = f"@{t_user} следит за:\n\n" + "".join(['@' + str(x) + '\n' for x in monitors])
                printed.append(t_user)
                update.message.reply_text(text)


def help(update: Update, contex: CallbackContext):
    text = "Бот уведомляет о новых подписках | отписках просматриваемых аккаунтов в инсте. Если кто-то сменит ник, то бот будет считать как |отписка+новая подписка|.ПРИВАТНЫЕ АККАУНТЫ НЕ ПРОСМАТРИВАЮТСЯ.\n\n" \
            "Команды:\n/set - Добавляет аккаунты для мониторинга.Пример:\n/set - biba @boba\n\n/unset - Убирает аккаунты из мониторинга.Пример:\n/unset @biba boba\n\n" \
            "/monitoring - Отображает все аккаунты, за которыми бот следит для вас"
    update.message.reply_text(text)

def check_privacity():
    for account in accounts_instagram:
        is_private = instagram.user_info(instagram.user_id_from_username(account.username)).is_private
        print(f"{account.username}: {is_private}")
        if is_private:
            remove_account(account)


telegram_dispatcher.add_handler(CommandHandler("set", set))
telegram_dispatcher.add_handler(CommandHandler("unset", unset))
telegram_dispatcher.add_handler(CommandHandler("monitorings", monitorings))
telegram_dispatcher.add_handler(CommandHandler("all_monitorings", all_monitorings))
telegram_dispatcher.add_handler(CommandHandler("help", help))
telegram_dispatcher.add_handler(CommandHandler("start", help))
telegram_updater.start_polling()
time.timezone = 3
lastTime = time.time()
while True:
    if (time.time - lastTime > 1800):
        check_privacity()
        check_accounts()
        lastTime = time.time()
    if (get_day() == 2):
        try_tuesday()
    elif (get_day() == 4):
        try_thursday()
telegram_updater.idle()
