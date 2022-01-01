import json


class InstAccount:
    def __init__(self, username,telegrams = [], followers = []):
        self.username = username
        self.telegrams = telegrams
        self.followers = followers

    def change_username(self, new_username):
        self.username = new_username

    def check_followers(self, data = []):
        new_followers = [user for user in data if user not in self.followers]
        unfollowers = [user for user in self.followers if user not in data]
        return new_followers, unfollowers

    def to_json(self):
        return {
            "telegrams": {i: self.telegrams[i] for i in range(0, len(self.telegrams))},
            "followers": {i: self.followers[i] for i in range(0, len(self.followers))}
        }
