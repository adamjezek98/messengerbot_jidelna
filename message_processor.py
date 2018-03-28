import sqlite3
import time
import botconfig
import sender
import send_menu
import os
import random
import user_manager
import class_scraper

os.chdir(botconfig.home_folder)
userManager = user_manager.UserManager()
classScraper = class_scraper.ClassScraper()


class MessageProcessor():
    db = sqlite3.connect(botconfig.db_path)
    c = db.cursor()

    def send_welcome(self, user_id):
        sender.send(sender.get_message_button_template(user_id,
                                                       "Ahoj!\nJsem bot, který by ti měl pomoct nepřehlédnout nic "
                                                       "důležitého. Kromě původního zasílání objedů nyní umím i "
                                                       "upozorňovat na suplování. Stačí si jenom nastavit třídu.",
                                                       (sender.get_postback_button("Ukaž jídelníček", "SENDCURRENT"),
                                                        sender.get_link_button("Nastavení",
                                                                               self.get_login_url(user_id)))))

    def send_whatyouneed(self, user_id):
        # print("====", user_id)
        sender.send(sender.get_message_button_template(user_id, "Potřebuješ něco?",
                                                       (sender.get_link_button("Nastavení",
                                                                               self.get_login_url(user_id)),
                                                        sender.get_postback_button("Jídelníček", "SENDCURRENT"),
                                                        sender.get_postback_button("Suplování", "SENDCLASS"))))

    def process_message(self, message):
        sender_id = message["sender"]["id"]
        print("=======process_message=========")

        try:
            message_text = message["message"]["text"]
        except:
            message_text = ""
            # další vůl posílá obrázky
            if self.reply_image(sender_id, message):
                return
        print(message_text, sender_id)
        if not userManager.user_exists(sender_id):  # nový uživatel
            self.send_welcome(sender_id)
            userManager.save_user(sender_id)
        else:

            if message_text.lower().replace("ž", "z").replace("á", "a").replace("í", "i") == "ukaz aktualni":
                self.fake_postback(sender_id, "SENDCURRENT")

            elif message_text.lower().replace("í", "i").replace("á", "a") == "suplovani":
                self.fake_postback(sender_id, "SENDCLASS")


            elif message_text.isdigit():  # custom čas
                if int(message_text) >= 0 and int(message_text) <= 23:
                    self.send_custom_subscribe_time(message_text, sender_id)
            elif isintext(message_text, ("diky", "díky", "děkuju", "dekuju", "děkuji", "dekuji", "dik", "dík")):
                dik = random.choice(
                    ("Nemusíš mi děkovat brouku :* <3", "Nemáš zač ;)", ":)", "No sem úžasnej, žejo?", "dik more"))
                sender.send_message(sender_id, dik)
                return
            elif message_text.lower().startswith("ne"):
                sender.send_message(sender_id, random.choice(("Když nic nepotřebuješ tak nepiš!","Co tim jako myslíš že ne?")))
                return


            else:  # klasická "Potřebuješ něco?"
                self.send_whatyouneed(sender_id)

    def fake_postback(self, userid, postback):
        self.process_postback({"recipient": {"id": userid},
                               "timestamp": int(time.time() * 1000),
                               "sender": {"id": userid},
                               "postback": {"payload": postback,
                                            "title": "Ano"}}
                              )

    def process_postback(self, postback):
        postback_type = postback["postback"]["payload"]
        sender_id = postback["sender"]["id"]
        self.c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
        user = self.c.fetchone()

        if postback_type == "SENDCURRENT":
            print("SENDCURRENT")
            send_menu.send_menu_to_one(sender_id)

        elif postback_type == "SENDCLASS":
            print("SENDCLASS")
            classScraper.send_from_db(sender_id)

    def reply_image(self, sender_id, message):
        print("no text")
        if "attachments" in message["message"].keys():
            print("attachment")
            for attach in message["message"]["attachments"]:
                print(attach)
                if attach["type"] == "image":
                    print("maybe image")
                    if "sticker_id" in attach["payload"].keys():
                        print("sticker")
                    else:
                        # sender.send_message(sender_id, "imgreptest")
                        img = random.choice(("rep1.gif", "rep2.gif", "bill.jpg", "rep1.jpg", "rep2.jpg"))
                        sender.send_image(sender_id,
                                          "https://archive.ajezek.cz/jidelna/" + img)
                        return True
        return False

    def get_login_url(self, userId):
        return "https://bot.ajezek.cz/login?uid=" + str(userId) + "&tk=" + userManager.get_user_login(userId)


def isintext(text, list):
    for l in list:
        if l.lower() in text.lower():
            return True
    return False
