import http.server
import ssl
import sqlite3
import datetime
import json
import botconfig
import sender
import send_menu
import os

os.chdir("/home/adam/messenger")

def send_welcome(user_id):
    sender.send(sender.get_message_button_template(user_id,
                                                   "Ahoj!\nZde se můžeš podívat na aktuální jídelníček, nebo se přihlásit k jeho pravidelnému odběru",
                                                   [["Odebírat", "SUBSCRIBE"], ["Ukaž aktuální", "SENDCURRENT"]]))


def send_modify(user_id):
    print("====", user_id)
    sender.send(sender.get_message_button_template(user_id,
                                                   "Potřebuješ něco?",
                                                   [["Zrušit odběr", "CANCELSUBSCRIBE"], ["Změnit čas", "SUBSCRIBE"],
                                                    ["Ukaž aktuální", "SENDCURRENT"]]))


def send_subscribe_time(user_id):
    sender.send(sender.get_message_button_template(user_id,
                                                   "V kolik chceš poslat jídelníček na následující dva obědy?\nV 7 ráno, v 11 před obědem, nebo v ve 4 odpoledne?",
                                                   [["7 ráno", "SUBSCRIBETIME7"], ["11 dopoledne", "SUBSCRIBETIME11"],
                                                    ["4 odoledne", "SUBSCRIBETIME16"]]))


class WebHandler(http.server.SimpleHTTPRequestHandler):
    # def log_message(self, format, *args):
    #    return
    def do_POST(self):
        length = int(self.headers['content-length'])
        print(self.path)
        data_string = str(self.rfile.read(length), "utf-8")
        print(data_string)
        j = json.loads(data_string)
        db = sqlite3.connect(botconfig.db_path)
        c = db.cursor()
        try:
            if "is_echo" in j["entry"][0]["messaging"][0]["message"].keys():
                if j["entry"][0]["messaging"][0]["message"]["is_echo"]:
                    print("not a message")
                    return
        except:
            pass
        if 1:
            sender_id = j["entry"][0]["messaging"][0]["sender"]["id"]
            c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
            user = c.fetchone()
            if "message" in j["entry"][0]["messaging"][0].keys():  # zprava
                print("message")
                if user == None:
                    send_welcome(sender_id)
                else:
                    send_modify(sender_id)
            elif "postback" in j["entry"][0]["messaging"][0].keys():  # postback
                print("payload")
                payload = j["entry"][0]["messaging"][0]["postback"]["payload"]
                if user == None and payload != "SENDCURRENT":
                    c.execute("INSERT INTO users VALUES(NULL, ?, NULL, NULL)", ([sender_id]))
                    db.commit()
                if payload == "SUBSCRIBE":
                    print("subscribe")
                    send_subscribe_time(sender_id)
                if payload.startswith("SUBSCRIBETIME"):
                    print("subscribetime")
                    t = payload.replace("SUBSCRIBETIME", "")
                    c.execute("UPDATE users SET 'hournotify'=? WHERE userid=?", ([t, sender_id]))
                    db.commit()
                    sender.send_message(sender_id, "Nastaveno. Jídelníček by ti měl přijít vždy v " + t + " hodin.")
                elif payload == "CANCELSUBSCRIBE":
                    c.execute("DELETE FROM users WHERE userid=?", ([sender_id]))
                    db.commit()
                    sender.send_message(sender_id, "Zrušeno")
                elif payload == "SENDCURRENT":
                    print("SENDCURRENT")
                    send_menu.send_menu_to_one(sender_id)

        # for webhook verify uncomment
        result = " "  # get_array["hub.challenge"][0]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(str(result), "utf-8"))

    def do_GET(self):
        result = "<meta charset='UTF-8'><h1>Jídelní lístek</h1><br/>"  # <h2>Školní jídelna Gymázium Roudnice nad Labem<h2/>"
        db = sqlite3.connect("database.sqlite3")
        c = db.cursor()
        c.execute("SELECT * FROM foods WHERE date >= julianday(?) ORDER BY date;",
                  ([datetime.date.today().strftime("%Y-%m-%d")]))
        result += '<table style="text-align: left;" border="1">'
        for r in c.fetchall():
            result += "<tr><th>" + r[2] + "</th><th>" + r[3].replace("\n", "<br/>") + "</th></tr>"
        result += "</table>"
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(str(result), "utf-8"))


server = http.server.HTTPServer(("0.0.0.0", 8080), WebHandler)
server.socket = ssl.wrap_socket(server.socket,
                                certfile=botconfig.certfile,
                                keyfile=botconfig.keyfile,
                                ca_certs=botconfig.ca_certs,
                                server_side=True)
server.serve_forever()
