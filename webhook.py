import http.server
import ssl
import sqlite3
import datetime
import json
import botconfig
import sender
import send_menu
import os
import message_processor

MessProc = message_processor.MessageProcessor()

os.chdir(botconfig.home_folder)

class WebHandler(http.server.SimpleHTTPRequestHandler):
    # def log_message(self, format, *args):
    #    return
    def do_POST(self):
        print("===========Webhook==========")
        length = int(self.headers['content-length'])
        print(datetime.datetime.now().strftime("%d. %m. %Y  %H:%M:%S"))
        print(self.path)
        data_string = str(self.rfile.read(length), "utf-8")
        print(data_string)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        print("=====headers_end======")
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
            #sender_id = j["entry"][0]["messaging"][0]["sender"]["id"]
            #c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
            #user = c.fetchone()
            if "message" in j["entry"][0]["messaging"][0].keys():  # zprava

                print("message")
                MessProc.process_message(j["entry"][0]["messaging"][0])

            elif "postback" in j["entry"][0]["messaging"][0].keys():  # postback
                print("payload")
                MessProc.process_postback(j["entry"][0]["messaging"][0])

        print("==========processing DONE===============")

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
#server.serve_forever()
while 1:
    try:
        server.handle_request()
    except:
        pass
