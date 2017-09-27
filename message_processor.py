import sqlite3
import time
import botconfig
import sender
import send_menu
import os

os.chdir(botconfig.home_folder)


class MessageProcessor():
    db = sqlite3.connect(botconfig.db_path)
    c = db.cursor()

    def send_welcome(self, user_id):
        sender.send(sender.get_message_button_template(user_id,
                                                       "Ahoj!\nZde se můžeš podívat na aktuální jídelníček, nebo se přihlásit k jeho pravidelnému odběru",
                                                       [["Odebírat", "SUBSCRIBE"], ["Ukaž aktuální", "SENDCURRENT"]]))

    def send_modify(self, user_id):
        print("====", user_id)
        sender.send(sender.get_message_button_template(user_id,
                                                       "Potřebuješ něco?",
                                                       [["Zrušit odběr", "CANCELSUBSCRIBE"],
                                                        ["Změnit čas", "SUBSCRIBE"],
                                                        ["Ukaž aktuální", "SENDCURRENT"]]))

    def send_subscribe_time(self, user_id):
        sender.send(sender.get_message_button_template(user_id,
                                                       "V kolik chceš poslat jídelníček na následující dva obědy?"
                                                       "\nTaké můžeš zvolit vlastní čas. Stačí napsat číslo v rozmezí 0-23",
                                                       [["7 ráno", "SUBSCRIBETIME7"],
                                                        ["11 dopoledne", "SUBSCRIBETIME11"],
                                                        ["4 odpoledne", "SUBSCRIBETIME16"]]))

    def send_custom_subscribe_time(self, time, user_id):
        sender.send(sender.get_message_button_template(user_id,
                                                       "Chceš si nechat zasílat jídelníček v " + time,
                                                       [["Ano", "SUBSCRIBETIME" + time],
                                                        ["Ne", "IGNORE"]]))

    def process_message(self, message):
        sender_id = message["sender"]["id"]
        self.c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
        user = self.c.fetchone()
        try:
            message_text = message["message"]["text"]
        except:
            message_text = ""

        if user == None:  # nový uživatel
            if message_text.lower().replace("í","i") == "odebirat":
                self.fake_postback(sender_id, "SUBSCRIBE")
            else: #uvitaci
                self.send_welcome(sender_id)
        else:

            if message_text.lower().replace("ž","z").replace("á","a").replace("í","i") == "ukaz aktualni":
                self.fake_postback(sender_id, "SENDCURRENT")

            elif message_text.lower().replace("í","i") == "odebirat":
                self.fake_postback(sender_id, "SUBSCRIBE")


            elif message_text.isdigit():  # custom čas
                if int(message_text) >= 0 and int(message_text) <= 23:
                    self.send_custom_subscribe_time(message_text, sender_id)


            else:  # klasická "Potřebuješ něco?"
                self.send_modify(sender_id)

    def fake_postback(self, userid, postback):
        self.process_postback({"recipient": {"id": userid},
                               "timestamp": int(time.time() * 1000),
                               "sender": {"id": "1508122325941445"},
                               "postback": {"payload": postback,
                                            "title": "Ano"}}
                              )

    def process_postback(self, postback):
        postback_type = postback["postback"]["payload"]
        sender_id = postback["sender"]["id"]
        self.c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
        user = self.c.fetchone()

        if user == None and postback_type in ("SUBSCRIBE", "SUBSCRIBETIME"):  # novy uzivatel
            self.c.execute("INSERT INTO users VALUES(NULL, ?, NULL, NULL)", ([sender_id]))
            self.db.commit()

        if postback_type == "SUBSCRIBE":  # posli subscribe volbu
            print("subscribe")
            self.send_subscribe_time(sender_id)

        elif postback_type.startswith("SUBSCRIBETIME"):  # nastaveni subscribe casu
            print("subscribetime")
            t = postback_type.replace("SUBSCRIBETIME", "")
            self.c.execute("UPDATE users SET 'hournotify'=? WHERE userid=?", ([t, sender_id]))
            self.db.commit()
            sender.send_message(sender_id, "Nastaveno. Jídelníček ti přijde vždy v " + t + " hodin.")

        elif postback_type == "CANCELSUBSCRIBE":  # zruseni odberu
            self.c.execute("DELETE FROM users WHERE userid=?", ([sender_id]))
            self.db.commit()
            sender.send_message(sender_id, "Zrušeno")

        elif postback_type == "SENDCURRENT":
            print("SENDCURRENT")
            send_menu.send_menu_to_one(sender_id)

        elif postback_type == "IGNORE":
            sender.send_message(sender_id, "Ok, budu to ignorovat")
