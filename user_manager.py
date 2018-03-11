import sqlite3
import time
import botconfig
import tools
import send_menu
import os
import hashlib
import requests

os.chdir(botconfig.home_folder)


class UserManager():
    db = sqlite3.connect(botconfig.db_path)
    c = db.cursor()

    def save_user(self, user_id):
        self.c.execute("INSERT INTO users(userid) VALUES(?)", ([user_id]))
        self.db.commit()

    def user_exists(self, user_id):
        self.c.execute("SELECT * FROM users WHERE userid=?", ([user_id]))
        user = self.c.fetchone()
        if user:
            return True
        return False

    def get_user_foodtime(self, user_id):
        self.c.execute("SELECT hournotify FROM users WHERE userid=?", ([user_id]))
        time = self.c.fetchone()[0]
        return time

    def get_user_classes(self, user_id):
        self.c.execute("SELECT room FROM class_notify WHERE userid=?", ([user_id]))
        classes = []
        for row in self.c.fetchall():
            classes.append(row[0])
        return classes

    def set_user_foodtime(self, user_id, foodtime):
        try:
            int(foodtime)
        except:
            foodtime = None
        self.c.execute("UPDATE users SET 'hournotify'=? WHERE userid=?", ([foodtime, user_id]))
        self.db.commit()

    def set_user_classeys(self, user_id, classes):
        self.c.execute("DELETE FROM class_notify WHERE userid=?", [user_id])
        c = []
        for cl in classes:
            c.append((user_id, tools.get_class_from_str(cl)))
        self.c.executemany("INSERT INTO class_notify(userid, room) VALUES (?,?)", c)
        self.db.commit()

    def get_user_login(self, user_id):
        token = hashlib.md5(bytes(str(user_id) + botconfig.secret_word, "utf8")).hexdigest()
        return token

    def check_user_login(self, user_id, token):
        orig_token = self.get_user_login(user_id)
        if (orig_token == token):
            # print(user_id, "login ok")
            return True
        # print(user_id, "login nok, expected",orig_token,"got",token)
        return False

    def get_user_profile_info(self, user_id):

        r = requests.get("https://graph.facebook.com/v2.6/" + str(user_id)
                         + "?fields=first_name,last_name,profile_pic&access_token=" + botconfig.messenger_access_token)
        r.encoding = "utf8"
        return r.text

