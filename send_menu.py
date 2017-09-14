import sqlite3
import datetime
import time

import os
import botconfig
import sender

os.chdir("/home/adam/messenger")




def get_current_menu():
    db =sqlite3.connect(botconfig.db_path)
    c = db.cursor()
    date = datetime.date.today().strftime("%Y-%m-%d")
    if int(time.strftime("%H")) > 15:
        c.execute("select * from foods where date > julianday(?) order by date limit 2",([date]))
    else:
        c.execute("select * from foods where date >= julianday(?) order by date limit 2",([date]))

    res  = ""
    for i in c.fetchall():
        res += i[2] + ":\n"+i[3]+"\n"
    return res

def send_menu_to_all():
    res = get_current_menu()
    if len(res) > 10:
        db = sqlite3.connect(botconfig.db_path)
        c = db.cursor()
        t = str(int(time.strftime("%H")))
        c.execute("select userid from users where  hournotify=?",([t]))
        for user in c.fetchall():
            sender.send_message(user[0],res)

def send_menu_to_one(userid):
    res = get_current_menu()
    sender.send_message(userid, res)

if __name__ == '__main__':
    send_menu_to_all()