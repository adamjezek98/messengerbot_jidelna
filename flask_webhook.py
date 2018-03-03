import http.server
import ssl
import sqlite3
import datetime
import json
import botconfig
import tools
import user_manager
import os
import message_processor

from flask import Flask, request, render_template, redirect, session

app = Flask(__name__)
app.config.from_object(__name__)

MessProc = message_processor.MessageProcessor()
userManager = user_manager.UserManager()
os.chdir(botconfig.home_folder)


@app.route("/")
def hello():
    if "user" not in session.keys():
        return render_template("login.html")
    return render_template("home.html")


@app.route("/login")
def login():
    arg = request.args
    print(arg)
    if ("uid" in arg.keys() and "tk" in arg.keys()):
        if userManager.check_user_login(arg["uid"], arg["tk"]):
            session["user"] = arg["uid"]
            return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/food_settings", methods=['GET', 'POST'])
@app.route("/food_settings/", methods=['GET', 'POST'])
def food_settings():
    if "user" not in session.keys():
        return render_template("login.html")
    if request.method == "GET":
        return render_template("food_settings.html", times=list(range(24)),
                               selected=userManager.get_user_foodtime(session["user"]))
    elif request.method == "POST":
        print(request.form["sendtime"])
        userManager.set_user_foodtime(session["user"], request.form["sendtime"])
        return redirect("/")


@app.route("/class_settings", methods=['GET', 'POST'])
@app.route("/class_settings/", methods=['GET', 'POST'])
def class_settings():
    if "user" not in session.keys():
        return render_template("login.html")
    if request.method == "GET":
        classes = {}
        for c in tools.get_classes():
            classes[c] = tools.get_class_str(c)
        return render_template("class_settings.html", classes=classes,
                               checked=userManager.get_user_classes(session["user"]))
    elif request.method == "POST":
        userManager.set_user_classeys(session["user"], list(request.form.keys()))
        return redirect("/")


@app.route("/webhook", methods=['GET', 'POST'])
# @app.route("/webhook/", methods=['GET', 'POST'])
def process_webhook():
    if request.method == "POST":
        print("===========Webhook==========")

        print(datetime.datetime.now().strftime("%d. %m. %Y  %H:%M:%S"))
        print(request.path)
        data_string = request.data
        print(data_string)

        j = json.loads(data_string)
        db = sqlite3.connect(botconfig.db_path)
        c = db.cursor()
        try:
            if "is_echo" in j["entry"][0]["messaging"][0]["message"].keys():
                if j["entry"][0]["messaging"][0]["message"]["is_echo"]:
                    print("not a message")
                    return "ok"
        except:
            pass
        if 1:
            # sender_id = j["entry"][0]["messaging"][0]["sender"]["id"]
            # c.execute("SELECT * FROM users WHERE userid=?", ([sender_id]))
            # user = c.fetchone()
            if "message" in j["entry"][0]["messaging"][0].keys():  # zprava

                print("message")
                MessProc.process_message(j["entry"][0]["messaging"][0])

            elif "postback" in j["entry"][0]["messaging"][0].keys():  # postback
                print("payload")
                MessProc.process_postback(j["entry"][0]["messaging"][0])

        print("==========processing DONE===============")
        return "ok"
    elif request.method == "GET":
        return "NO humans please"


if __name__ == "__main__":
    app.secret_key = botconfig.secret_word
    app.run(host="0.0.0.0", port=5020)
