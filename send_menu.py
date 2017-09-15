import sqlite3
import datetime
import time

import os
import botconfig
import sender

os.chdir(botconfig.home_folder)




def get_current_menu(days=2,rawreturn=False):
    db =sqlite3.connect(botconfig.db_path)
    c = db.cursor()
    date = datetime.date.today().strftime("%Y-%m-%d")
    if int(time.strftime("%H")) > 15:
        c.execute("select * from foods where date > julianday(?) order by date limit ?",([date,days]))
    else:
        c.execute("select * from foods where date >= julianday(?) order by date limit ?",([date,days]))

    res  = ""
    if rawreturn:
        return  c.fetchall()
    for i in c.fetchall():
        res += i[2] + ":\n"+i[3]+"\n\n"
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

def send_menu_to_one(userid,days=5):
    res = get_current_menu(days)
    sender.send_message(userid, res)

def publish_menu_to_page(days=2):
    menu = "Jídelníček na následující obědy:\n"
    for i in get_current_menu(days, True):
        menu += "V " + i[2] + " bude " + i[3] + "\n\n"
    menu += "\nKompletní jídelníček najdete na adrese wwwajezek.cz:8000\n"

    sender.publish_post(menu)

if __name__ == '__main__':
    if datetime.datetime.weekday(datetime.datetime.today()) not in (5,6):
        send_menu_to_all()
    if datetime.datetime.weekday(datetime.datetime.today()) not in (4,5) & int(time.strftime("%H")) == 20:
        publish_menu_to_page()



