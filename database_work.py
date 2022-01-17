from inst_account import InstAccount
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
import os

connection = psycopg2.connect(user="mpyebwhixhtcmy", password="5d8c92b8a9848ea60c84757c30e225e4f14829552c027a787556bb66ce25d1a3",
                              host="ec2-54-83-157-174.compute-1.amazonaws.com", port="5432", dbname="d7la9jmdc5vd0b")
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()


def load_accounts():
        accounts = []
        cursor.execute("SELECT * FROM monitor_account")
        data = cursor.fetchall()
        for acc in data:
                accounts.append(InstAccount(acc[0].strip(), acc[1], [str(x).strip() for x in acc[3]], [x.strip() for x in acc[2]]))
        return accounts

print([account.telegram_username for account in load_accounts()])

def remove_account(account: InstAccount):
        cursor.execute(f"DELETE FROM monitor_account WHERE username = '{account.username}'")
        connection.commit()


def save_account(account: InstAccount):
        cursor.execute(f"SELECT * FROM monitor_account WHERE username = '{account.username}'")
        if cursor.rowcount > 0:
                cursor.execute(f"UPDATE monitor_account SET telegrams = %s, t_username = %s, followers = %s WHERE username = %s",
                               (account.telegrams, account.telegram_username, account.followers, account.username))
        else:
                cursor.execute(f"INSERT INTO monitor_account (USERNAME, TELEGRAMS, T_USERNAME, FOLLOWERS) VALUES (%s, %s, %s, %s)",
                               (account.username, account.telegrams, account.telegram_username, account.followers))
        connection.commit()
