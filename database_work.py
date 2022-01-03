from inst_account import InstAccount
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2

connection = psycopg2.connect(user="timfors", password="weas2222", host="localhost", port="5432", dbname="insta")
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = connection.cursor()


def load_accounts():
        accounts = []
        cursor.execute("SELECT * FROM monitor_account")
        data = cursor.fetchall()
        for acc in data:
                accounts.append(InstAccount(acc[0].strip(), acc[1], [x.strip() for x in acc[3]], [x.strip() for x in acc[2]]))
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
